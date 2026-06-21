import { app, BrowserWindow, screen } from 'electron';

function createWindow() {
  // Get the full size of the user's monitor
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;

  const win = new BrowserWindow({
    x: 0,
    y: 0,
    width: width,
    height: height,
    transparent: true,      // Makes the background invisible
    frame: false,           // Removes the Windows title bar
    alwaysOnTop: true,      // Forces it to stay over Zoom/Teams
    skipTaskbar: true,      // Hides it from the taskbar
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  // CRITICAL: Makes the window "click-through" so it doesn't block the user's mouse!
  win.setIgnoreMouseEvents(true, { forward: true });

  // Load the React app
  win.loadURL('http://localhost:5173');
}

app.whenReady().then(createWindow);