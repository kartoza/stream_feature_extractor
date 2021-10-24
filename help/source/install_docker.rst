.. _plugin_testing-label:

Docker
======

If the user wants to test the plugin for issues/errors, Docker needs to be installed. The installation
steps differs in Linux and Windows. The first section deals with Linux, which is followed by instructions on how
to perform the installation in Windows.

Install in Linux
----------------
Docker is required to perform testing. So if the user does not have docker installed, they need to do the following:

    1. Open terminal in Linux.

    2. Run the following commands in the console:

        a. sudo apt-get update

        b. sudo apt-get install \\

            curl \\

            gnupg \\

            lsb-release

    3. curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    4. echo \\
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
More detailed instructions for installation and other options can be found here: https://docs.docker.com/engine/install/ubuntu/

Install in Windows
------------------
Here is the installation instructions for use of Docker in Windows:

    1. Download the Docker Desktop installation for Windows: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe.

    2. Double-click on the exe once it finished downloading. The installer will first unpack the files.

    3. Enable Hyper-V Windows Features or Install required Windows componets for WSL 2 during the installation steps.

    4. Once the installer is done, click on Close.

Additional steps will be required if your Windows login account is not he administrator:

1. Open the Computer Manager: Type 'computer manager' in the Windows start menu and open it.

2. Go to System Tools > Local Users and Groups:

   .. image:: /examples/computer_manager.png
      :align: center

3. Double-click on the 'docker-users' to open the properties of the group:

   .. image:: /examples/docker_properties.png
      :align: center

4. Click on the Add button to add your user name:

   .. image:: /examples/add_user.png
      :align: center

5. Add your user name and click on the OK button.

6. Docker is now installed.

More detailed instructions on installing Docker in Windows can be found here: https://docs.docker.com/desktop/windows/install/
