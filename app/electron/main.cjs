'use strict';

const fs = require('node:fs');
const path = require('node:path');
const {
  app,
  BrowserWindow,
  Menu,
  ipcMain,
  nativeTheme,
  protocol,
  shell,
} = require('electron');

const APP_SCHEME = 'app';
const APP_HOST = 'bundle';
const APP_ORIGIN = `${APP_SCHEME}://${APP_HOST}`;
const PORTABLE_DATA_DIR_NAME = 'radiative-cooling-data';
const TITLE_BAR_HEIGHT = 52;
const EXTERNAL_PROTOCOLS = new Set(['http:', 'https:', 'mailto:']);

protocol.registerSchemesAsPrivileged([
  {
    scheme: APP_SCHEME,
    privileges: {
      standard: true,
      secure: true,
      supportFetchAPI: true,
      stream: true,
      codeCache: true,
    },
  },
]);

if (process.env.PORTABLE_EXECUTABLE_DIR) {
  const portableDataPath = path.join(process.env.PORTABLE_EXECUTABLE_DIR, PORTABLE_DATA_DIR_NAME);
  fs.mkdirSync(portableDataPath, { recursive: true });
  app.setPath('userData', portableDataPath);
}

const sessionDataPath = path.join(app.getPath('userData'), 'session');
fs.mkdirSync(sessionDataPath, { recursive: true });
app.setPath('sessionData', sessionDataPath);

let mainWindow = null;

function getDistDir() {
  return path.join(app.getAppPath(), 'dist');
}

function getPreloadPath() {
  return path.join(app.getAppPath(), 'electron', 'preload.cjs');
}

function getMimeType(filePath) {
  switch (path.extname(filePath).toLowerCase()) {
    case '.html':
      return 'text/html; charset=utf-8';
    case '.js':
    case '.mjs':
    case '.cjs':
      return 'text/javascript; charset=utf-8';
    case '.css':
      return 'text/css; charset=utf-8';
    case '.json':
      return 'application/json; charset=utf-8';
    case '.svg':
      return 'image/svg+xml';
    case '.png':
      return 'image/png';
    case '.jpg':
    case '.jpeg':
      return 'image/jpeg';
    case '.webp':
      return 'image/webp';
    case '.ico':
      return 'image/x-icon';
    case '.pdf':
      return 'application/pdf';
    case '.woff':
      return 'font/woff';
    case '.woff2':
      return 'font/woff2';
    case '.txt':
      return 'text/plain; charset=utf-8';
    default:
      return 'application/octet-stream';
  }
}

function isExternalUrl(targetUrl) {
  try {
    return EXTERNAL_PROTOCOLS.has(new URL(targetUrl).protocol);
  } catch {
    return false;
  }
}

function getResolvedSystemTheme() {
  return nativeTheme.shouldUseDarkColors ? 'dark' : 'light';
}

function getWindowBackground(theme) {
  return theme === 'dark' ? '#1d2722' : '#f5f3ef';
}

function getTitleBarOverlay(theme) {
  return {
    color: '#00000000',
    symbolColor: theme === 'dark' ? '#f7f2e7' : '#1f2b24',
    height: TITLE_BAR_HEIGHT,
  };
}

function applyWindowAppearance(targetWindow, theme = getResolvedSystemTheme()) {
  if (!targetWindow || targetWindow.isDestroyed()) {
    return;
  }

  targetWindow.setBackgroundColor(getWindowBackground(theme));

  if (typeof targetWindow.setTitleBarOverlay === 'function') {
    targetWindow.setTitleBarOverlay(getTitleBarOverlay(theme));
  }
}

function registerProtocolHandler(distDir) {
  protocol.handle(APP_SCHEME, async (request) => {
    const requestUrl = new URL(request.url);
    const relativePath = requestUrl.pathname === '/'
      ? 'index.html'
      : requestUrl.pathname.replace(/^\/+/, '');
    const filePath = path.join(distDir, relativePath);

    try {
      const payload = await fs.promises.readFile(filePath);
      return new Response(new Uint8Array(payload), {
        headers: {
          'content-type': getMimeType(filePath),
        },
      });
    } catch (error) {
      if (!path.extname(relativePath)) {
        const fallbackPath = path.join(distDir, 'index.html');
        const payload = await fs.promises.readFile(fallbackPath);
        return new Response(new Uint8Array(payload), {
          headers: {
            'content-type': getMimeType(fallbackPath),
          },
        });
      }

      console.error('Failed to serve bundled asset.', request.url, error);
      return new Response('Not found', {
        status: 404,
        headers: { 'content-type': 'text/plain; charset=utf-8' },
      });
    }
  });
}

async function createMainWindow() {
  const resolvedTheme = getResolvedSystemTheme();

  mainWindow = new BrowserWindow({
    title: 'Radiative Cooling Explorer',
    width: 1440,
    height: 960,
    minWidth: 1100,
    minHeight: 720,
    backgroundColor: getWindowBackground(resolvedTheme),
    autoHideMenuBar: true,
    titleBarStyle: 'hidden',
    titleBarOverlay: getTitleBarOverlay(resolvedTheme),
    show: false,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      preload: getPreloadPath(),
    },
  });

  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
  });

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (isExternalUrl(url)) {
      void shell.openExternal(url);
      return { action: 'deny' };
    }

    return { action: 'allow' };
  });

  mainWindow.webContents.on('will-navigate', (event, url) => {
    if (!isExternalUrl(url)) {
      return;
    }

    event.preventDefault();
    void shell.openExternal(url);
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  await mainWindow.loadURL(`${APP_ORIGIN}/`);
  return mainWindow;
}

nativeTheme.on('updated', () => {
  applyWindowAppearance(mainWindow);
});

ipcMain.on('desktop:set-window-theme', (event, theme) => {
  if (theme !== 'light' && theme !== 'dark') {
    return;
  }

  const senderWindow = BrowserWindow.fromWebContents(event.sender);
  applyWindowAppearance(senderWindow, theme);
});

app.whenReady().then(async () => {
  Menu.setApplicationMenu(null);
  registerProtocolHandler(getDistDir());
  await createMainWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      void createMainWindow();
    }
  });
}).catch((error) => {
  console.error('Failed to start Electron shell.', error);
  app.exit(1);
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
