XBlock SimpleJudge
=========================
Introduction
------------
XBlock SimpleJudge is a plugin for training students' programming skill in edx

Installation
------------
**1. Install Open edx platform**

  Github:
  
  https://github.com/edx/edx-platform

  Instruction:
  
  https://openedx.atlassian.net/wiki/display/OpenOPS/Running+Devstack

**2. Install SimpleJudge and the requirements of it**
  ``` 
  sudo apt-get install python3
  
  cd /edx/xblock-simplejudge/
  sudo -H -u edxapp bash
  source /edx/app/edxapp/venvs/edxapp/bin/activate
  pip install -r requirements.txt
  ```

**3. Restart cms/lms server**
  ```
  sudo /edx/bin/supervisorctl restart edxapp:
  ```
