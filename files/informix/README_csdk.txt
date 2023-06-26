IBM® Informix® ClientSDKV 4.50

Common installation methods:
	The commands below describe basic installation methods. The IBM ClientSDK Installation Guide contains detailed information about how to set up Informix for your needs.
	Available at https://www.ibm.com/support/knowledgecenter/SSGU8G/welcomeIfxServers.html
	Run this command to install Informix in graphical mode:
		installclientsdk -gui
	Alternately, to install Informix in console mode:
		installclientsdk -console

Known Install issue (and workaround):
	Unix/Linux: Systems with Minimal OS installed can have problems launching Installer.

		% sudo ./ids_install
		Preparing to install
		Extracting the JRE from the installer archive...
		Unpacking the JRE...
		Extracting the installation resources from the installer archive...
		Configuring the installer for this system's environment...

		Launching installer...


		=======================================================

		Installer User Interface Mode Not Supported

		Unable to load and to prepare the installer in console or silent mode.

		=======================================================

	The problem can show up on machines with certain combinations of installed fonts.

	To Workaround this problem you can:
		Install some non-CFF font on the machine. With this, it should be possible to avoid the problem with the Java VM by installing an additional, non-CFF font, i.e. a font of a format that is not CFF.

		The following has been successful on RedHat systems Linux x86_64 and Linux POWER8 Little Endian:
		% fc-match -f "sans:regular:roman" -sv  # lists only fonts of format type CFF
		% sudo yum install gnu-free-mono-fonts  # install a non-CFF font
