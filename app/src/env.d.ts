interface RcDesktopApi {
  isDesktopShell: boolean
  setWindowTheme: (theme: 'light' | 'dark') => void
}

interface Window {
  rcDesktop?: RcDesktopApi
}
