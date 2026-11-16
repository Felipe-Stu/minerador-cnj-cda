const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn, spawnSync } = require('child_process');

let flask = null;


function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  win.loadURL('http://localhost:5000/mineradora');
}


function iniciarFlask() {
  // Python do ambiente virtual do projeto, executado sem shell para poder ser encerrado
  const pythonPath = path.join(__dirname, '..', '.venv', 'Scripts', 'python.exe');

  flask = spawn(pythonPath, ['main.py'], {
    cwd: path.join(__dirname, '..'),
    env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
  });

  flask.stdout.on('data', (data) => console.log(`[FLASK] ${data}`));
  flask.stderr.on('data', (data) => console.error(`[FLASK ERROR] ${data}`));
  flask.on('error', (err) => console.error(`[FLASK ERROR] ${err.message}`));
}

app.whenReady().then(() => {
  iniciarFlask();
  setTimeout(createWindow, 2000);
});

// Encerra o servidor Flask junto com a janela.
// No Windows, o python.exe do .venv é um lançador que abre o Python real como
// processo filho; por isso é preciso encerrar a árvore inteira (/T).
function encerrarFlask() {
  if (!flask || flask.exitCode !== null) return;
  if (process.platform === 'win32') {
    spawnSync('taskkill', ['/PID', String(flask.pid), '/T', '/F']);
  } else {
    flask.kill();
  }
  flask = null;
}

app.on('window-all-closed', () => {
  encerrarFlask();
  app.quit();
});

app.on('before-quit', encerrarFlask);

const { ipcMain, dialog } = require('electron');

ipcMain.on('abrir-dialogo', async (event) => {
  const { canceled, filePaths } = await dialog.showOpenDialog({
    title: 'Selecione um arquivo CSV',
    filters: [{ name: 'CSV Files', extensions: ['csv'] }],
    properties: ['openFile']
  });

  if (!canceled && filePaths.length > 0) {
    const caminho = filePaths[0];
    event.sender.send('arquivo-selecionado', caminho);
  }
});

