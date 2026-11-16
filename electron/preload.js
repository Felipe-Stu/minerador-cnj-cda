const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  selecionarArquivo: () => ipcRenderer.send('abrir-dialogo')
});

contextBridge.exposeInMainWorld('electronAPIReceber', (callback) => {
  ipcRenderer.on('arquivo-selecionado', (event, caminho) => callback(caminho));
});
