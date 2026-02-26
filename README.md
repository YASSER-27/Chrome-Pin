# Chrome View Controller

**Chrome View Controller** is a professional productivity utility designed to reconfigure Google Chrome windows into a streamlined, "chat-style" interface. It enhances multitasking efficiency by maintaining selected web windows in an elongated vertical aspect ratio, pinning them to the foreground, and docking them to the screen periphery.

---

## Technical Specifications

| Feature | Functionality |
| :--- | :--- |
| **Foreground Priority** | Implements deep Windows API calls to maintain "Always on Top" status over all system applications. |
| **Optimized Geometry** | Automatically recalibrates window dimensions to 400x900, forcing a mobile-responsive web view. |
| **Command Shortcut** | Integrated `Ctrl + G` global hotkey to invoke the window selection menu instantly. |
| **State Restoration** | Automated "Clean Exit" logic that reverts all modified windows to their original dimensions and styles. |
| **Background Operation** | Low-overhead execution via the System Tray with zero interference to the primary workspace. |

---

## Visual Presentation

### Interface Overview
> [!NOTE]  
> The following assets demonstrate the transformation from a standard browser tab to a docked vertical interface.

| Application Icon | Transformation Logic | GUI Interface |
| :---: | :---: | :---: |
| ![Icon](high.png) | ![IMAGE](example/example.png) | ![IMAGE](example/example_gui.png) |

### Functional Demonstration

<p align="center">
  <video src="https://github.com/user-attachments/assets/6b3b61c5-63ea-4d43-b69b-d5d8a68195ae" width="100%" autoplay loop muted playsinline>
  </video>
</p>

---

<p align="center">
  <video src="https://github.com/user-attachments/assets/557d6eaa-9135-4b1b-84f5-121848dc4ea8" width="100%" autoplay loop muted playsinline>
  </video>
</p>

---

## Operational Workflow

1. **Initialization**: Execute the application binary or source script.
2. **Selection**: Invoke the selection menu via `Ctrl + G` or the System Tray context menu.
3. **Transformation**: Identify and select the target Google Chrome window for conversion.
4. **Utilization**: The window is now anchored in the foreground, providing persistent access while working in other environments.
5. **Termination**: Selecting "Exit" will trigger a global reset, restoring all managed windows to their default system states.

---

## Distribution

[![Download Latest Release](https://img.shields.io/badge/DOWNLOAD-LATEST_RELEASE-0078d4?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/YASSER-27/Chrome-Pin/releases)  

---

## Developer Documentation

### Prerequisites
To execute the source code directly, the following Python environment and libraries are required:

```bash
pip install PyQt6 pygetwindow pywin32
