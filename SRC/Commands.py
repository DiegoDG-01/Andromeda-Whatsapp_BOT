##############################################
##############################################
##                                          ##
##   _______ _____  ______ _____ _______    ##
##   |______   |   |_____/   |   |______    ##
##   ______| __|__ |    \_ __|__ ______|    ##
##                                          ##
##             Command Manager              ##
##                                          ##
##############################################
##############################################

# Module imported from the main python library
import Log
from re import match
from os import getcwd
from json import load
from json import JSONDecodeError

# Modules to import from the project
import Functions.Help
import Functions.Configure
import Functions.AutomatedMessages


class CommandManager:

    # (InterfaceController) Interface instance to control the web whatsapp interface
    # this instance is only used to some modules
    # Is added from the line #56 and onwards
    def __init__(self, Communicate, InterfaceController, Schedule):

        # Log instance
        self.Log = Log.Generate()

        # Save Communicate to permit communicate with user in whatsapp

        self.command = None
        self.commands = None
        self.commandargs = None
        self.commandInfo = None
        self.Path = getcwd() + '/Data/Config/Codes.json'

        with open(self.Path, 'r') as File:
            try:
                self.commands = load(File)
            except JSONDecodeError as err:
                self.Log.Write("Commands.py | JSONDecodeError # " + str(err))
                exit(1)
            finally:
                File.close()

        # Load module help
        self.Help = Functions.Help.Help(self.commands, Communicate)
        # Load module config
        self.Config = Functions.Configure.Configure(self.commands, Communicate)
        # Load module automated messages
        # Add the interface controller to the automated messages
        # and the pass the schedule to used function to reset the schedule and
        # load the new schedule
        # (Schedule) Schedule is only used to reset the schedule in necessary modules
        self.AutomatedMessages = Functions.AutomatedMessages.AutomatedMessages(self.commands, Communicate, InterfaceController, Schedule)

        # List of all modules loaded
        self.ListAction = {
            "/help": self.Help.EntryPoint,
            "/config": self.Config.EntryPoint,
            "/AutoMessage": self.AutomatedMessages.EntryPoint
        }

    def Get_List_of_Functions(self):
        return self.ListAction


    def Read(self, command):

        """[summary]

        Returns:
            [type]: [description]
        """

        # save command
        self.command = command[0]
        # remove command position
        command.pop(0)
        # save command args
        self.commandargs = command

        if self.__IsCommand():

            IsValid, info = self.__IsValidCommand()

            return IsValid, info
        else:
            return False, None

    def Execute(self):

        """[summary]

        Returns:
            [type]: [description]
        """

        if self.commandargs:
            contentargs, error = self.__ContentArgs()

            if contentargs is True and error is None:
                return self.ListAction[self.command](self.commandargs), None
            else:
                return contentargs, error
        else:
            # return self.ListAction[self.command][2](self.Communicate), None
            return self.ListAction[self.command](), None

    def __IsCommand(self):

        """[summary]

        Returns:
            [type]: [description]
        """

        regex = "^/[a-zA-Z]+$"

        isCommand = match(regex, self.command)

        if isCommand is not None:
            return True
        else:
            return False

    def __IsValidCommand(self):

        """[summary]

        Returns:
            [type]: [description]
        """

        if self.command in self.commands['Active']:
            self.commandInfo = self.commands['Active'][self.command]
            return True, None
        elif self.command in self.commands['Development']:
            self.commandInfo = self.commands['Development'][self.command]
            return True, "Command in development"
        else:
            return False, 'Invalid command'

    def __ContentArgs(self):

        """[summary]

        Returns:
            [type]: [description]
        """

        if self.commandargs:

            if self.commandargs[0] in self.commands['Active'][self.command]["Args"][0].keys():
                return True, None
            else:
                return False, "Invalid argument"
        else:
            return False, "Argument not exist"
