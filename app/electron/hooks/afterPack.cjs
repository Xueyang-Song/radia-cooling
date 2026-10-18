'use strict';

const fs = require('node:fs');
const path = require('node:path');

module.exports = async function afterPack(context) {
  const defaultSnapshotPath = path.join(context.appOutDir, 'v8_context_snapshot.bin');
  const browserSnapshotPath = path.join(context.appOutDir, 'browser_v8_context_snapshot.bin');

  if (!fs.existsSync(defaultSnapshotPath)) {
    throw new Error(`Electron did not provide ${defaultSnapshotPath}`);
  }

  await fs.promises.copyFile(defaultSnapshotPath, browserSnapshotPath);
};

module.exports.default = module.exports;
