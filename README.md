# vfx_cams
Aimed to create a set of tools to control multiple cameras to help VFX workflow, start with photogrammetry, maybe bullet time later. I got some of Sony NEX cameras, and Sony has API to control them, so I started from them.

This is rush personal project originally, moved from private repo to public and looking for anyone (VFX Artist, Developer, Designer, Engineer & Everyone) would like to join the development, welcome for comments, create issues, fork, pull request & others.

This Project is logging in https://hackaday.io/project/189006

Work In Progress: Rewrite all code, Redesign the UI.

## ⚙️ Backend
- Two side of backend, controller and server side
- Controller side is running on SBC (Orange pi Zero 2) to control the camera by Sony Camera Remote API (https://developer.sony.com/develop/cameras/)
- For 30 cameras, there will be 30 controller run on 30 SBC
- Server side is running on any computer by sending command to all Controllers
- Both controller and server side: Running python flask to handle POST JSON command from control panal UI(frontend)
- pysony (https://github.com/Bloodevil/sony_camera_api) is used to handle Sony's API

## 🎨 Frontend
- Bootstrap is used for UI layout
- Jquery is used for handle button actions
- Jinja format templates for flask in python

## 🛠 Setup for Development

#### Setup Python3 & Virtualenv
Update Homebrew (Optional)
```bash
brew update
```

Install Python3
```bash
brew install python3
```

Install Virtualenv
```bash
pip3 install virtualenv
```

Go to Project folder
```bash
cd <project-folder-path>
```

Create Virtualenv and Activate
```bash
virtualenv -p python3 venv
source venv/bin/activate
```

Install Python Modules
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 💻 Developing Environment
#### System
- macOS Monterey 12.4
- Homebrew (https://brew.sh/)
- Bootstrap Studio 6.1.2 (https://bootstrapstudio.io/)

#### Python
- Python 3.10.8 (https://www.python.org/)
- virtualenv 20.17.1 (https://virtualenv.pypa.io/)

#### Python Modules (requirements.txt)
- opencv-python >= 4.6.0.66 # https://pypi.org/project/opencv-python/
- requests >= 2.28.1 # https://pypi.org/project/requests/
- Flask >= 2.2.2 # https://pypi.org/project/Flask/
- asyncio >= 3.4.3 # https://pypi.org/project/asyncio/
- aiohttp >= 3.8.3 # https://pypi.org/project/aiohttp/
- beautifulsoup4 >= 4.11.1 # https://pypi.org/project/beautifulsoup4/
- #pysony == 0.1.12 (Manual install from https://github.com/Bloodevil/sony_camera_api)

#### Frontend
- Bootstrap v5.2 (https://getbootstrap.com/)
- Bootstrap Icons v1.8.0 (https://icons.getbootstrap.com/)
- JQuery v3.6.0 (https://jquery.com/)
- gridstrap.js v0.7.3 (https://github.com/rosspi/gridstrap.js)

## ⚖️ License
© 2022 Addie Liu (liuaddie@gmail.com)

**GNU Lesser General Public License (LGPL) v3.0:** Contributor(s) distributes one or more Open Source Components with the Software, which either operates as distinct processes that run in parallel with the Software or are dynamic libraries that are interacted with by the Software at runtime under the LGPL v3.0. A copy of the GNU Lesser General Public License v3.0 may be found at https://www.gnu.org/licenses/lgpl-3.0.html.
