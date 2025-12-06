# M208 IDP repository
Please read this file for important setup instructions

This branch has the code that actually ran in the robot, which can be read in /IDP/modules. The file graph_model.py is an exception: it has about 7 lines that were reconstructed from memory, since these very last changes were not saved. They are very likely to be faithful.
## Prerequisites
- Thonny
- Git

## Setup Instructions
### Thonny
- Download Thonny from https://thonny.org/
- Open Thonny > bottom right > Select Interpreter > MicroPython (Raspberry Pi Pico)

### VSCode
- Unsure if this works.
- To setup:
`code --install-extension ms-python.python`
`code --install-extension visualstudioexptteam.vscodeintellicode`
`code --install-extension ms-python.vscode-pylance`
`code --install-extension paulober.pico-w-go`

- To launch: `export PICO_SDK_PATH=/home/pi/pico/pico-sdk` -->
`code`

## Version Control Practices
1. Commit every significant change. If unsure, err on the side of committing too much rather than too little.
2. Add a helpful commit message to EVERY commit so that people know what is going on/what has been changed.
3. Work on your own branch and resolve conflicts carefully before merging into `main`.
