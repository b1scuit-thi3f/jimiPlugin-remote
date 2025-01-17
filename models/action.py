from core import settings, helpers, auth
from core.models import action
from plugins.remote.includes import linux, windows, fortigate, cisco
import re
import jimi

class _remoteConnectLinux(action._action):
    host = str()
    user = str()
    keyfile = str()
    password = str()
    port = 22
    remote_port = str()
    isPortForward = bool()
    timeout = 10
    enable_scp = True
    
    def doAction(self,data):
        host = helpers.evalString(self.host,{"data" : data["flowData"]})
        user = helpers.evalString(self.user,{"data" : data["flowData"]})
        remote_port = helpers.evalString(self.remote_port,{"data" : data["flowData"]})
        if not remote_port:
            remote_port = 22
        if self.password.startswith("ENC") and self.password != "":
            password = auth.getPasswordFromENC(self.password)
        elif "%%" in self.password:
            password = helpers.evalString(self.password,{"data" : data["flowData"]})
        else:
            password = ""
        keyfile = helpers.evalString(self.keyfile,{"data" : data["flowData"]})

        if self.isPortForward:
            if keyfile != "":
                if password:
                    client= linux.linux(host,user,keyFile=keyfile,password=password,port=self.port,port_forward=True,remote_port=remote_port,timeout=self.timeout,enable_scp=self.enable_scp)
                else:
                    client = linux.linux(host,user,keyFile=keyfile,port=self.port,port_forward=True,remote_port=remote_port,timeout=self.timeout,enable_scp=self.enable_scp)
            else:
                client = linux.linux(host,user,password=password,port=self.port,timeout=self.timeout,enable_scp=self.enable_scp)
        else:
            if keyfile != "":
                if password != "":
                    client = linux.linux(host,user,keyFile=keyfile,password=password,port=self.port,timeout=self.timeout,enable_scp=self.enable_scp)
                else:
                    client = linux.linux(host,user,keyFile=keyfile,port=self.port,timeout=self.timeout,enable_scp=self.enable_scp)
            else:
                client = linux.linux(host,user,password=password,port=self.port,timeout=self.timeout,enable_scp=self.enable_scp)

        if client.client != None:
            data["eventData"]["remote"]={}
            data["eventData"]["remote"]["client"] = client

            if self.isPortForward:
                data["eventData"]["remote"]["port"] = client.tunnelPort
            return {"result" : True, "rc" : 0, "msg" : "Connection successful"}
        else:
            return {"result" : False, "rc" : 403, "msg" : "Connection failed - {0}".format(client.error)}

    def setAttribute(self,attr,value,sessionData=None):
        if attr == "password" and not value.startswith("ENC ") and not re.match(".*%%.*%%",value):
            self.password = "ENC {0}".format(auth.getENCFromPassword(value))
            return True
        return super(_remoteConnectLinux, self).setAttribute(attr,value,sessionData=sessionData)

class _remoteConnectWindows(action._action):
    host = str()
    user = str()
    password = str()
    enable_smb = True

    def doAction(self,data):
        host = helpers.evalString(self.host,{"data" : data["flowData"]})
        user = helpers.evalString(self.user,{"data" : data["flowData"]})
        if self.password.startswith("ENC"):
            password = auth.getPasswordFromENC(self.password)
        elif "%%" in self.password:
            password = helpers.evalString(self.password,{"data" : data["flowData"]})

        client = windows.windows(host,user,password,smb=self.enable_smb)
        if client.client != None:
            data["eventData"]["remote"]={"client" : client}
            return {"result" : True, "rc" : 0, "msg" : "Connection successful"}
        else:
            return {"result" : False, "rc" : 403, "msg" : "Connection failed - {0}".format(client.error)}

    def setAttribute(self,attr,value,sessionData=None):
        if attr == "password" and not value.startswith("ENC ") and not re.match(".*%%.*%%",value):
            self.password = "ENC {0}".format(auth.getENCFromPassword(value))
            return True
        return super(_remoteConnectWindows, self).setAttribute(attr,value,sessionData=sessionData)

class _remoteConnectWindowsPSExec(action._action):
    host = str()
    user = str()
    password = str()
    use_encryption = True

    def doAction(self,data):
        host = helpers.evalString(self.host,{"data" : data["flowData"]})
        user = helpers.evalString(self.user,{"data" : data["flowData"]})
        if self.password.startswith("ENC"):
            password = auth.getPasswordFromENC(self.password)
        elif "%%" in self.password:
            password = helpers.evalString(self.password,{"data" : data["flowData"]})

        client = windows.windowsPSExec(host,user,password,self.use_encryption)
        if client.client != None:
            data["eventData"]["remote"]={"client" : client}
            return {"result" : True, "rc" : 0, "msg" : "Connection successful"}
        else:
            return {"result" : False, "rc" : 403, "msg" : "Connection failed - {0}".format(client.error)}

    def setAttribute(self,attr,value,sessionData=None):
        if attr == "password" and not value.startswith("ENC ") and not re.match(".*%%.*%%",value):
            self.password = "ENC {0}".format(auth.getENCFromPassword(value))
            return True
        return super(_remoteConnectWindowsPSExec, self).setAttribute(attr,value,sessionData=sessionData)

class _remoteConnectFortigate(action._action):
    host = str()
    port = str()
    deviceHostname = str()
    user = str()
    password = str()
    timeout = 5

    def doAction(self,data):
        host = helpers.evalString(self.host,{"data" : data["flowData"]})
        port = helpers.evalString(self.port,{"data" : data["flowData"]})
        if not port:
            port = 22
        deviceHostname = helpers.evalString(self.deviceHostname,{"data" : data["flowData"]})
        user = helpers.evalString(self.user,{"data" : data["flowData"]})
        if self.password.startswith("ENC"):
            password = auth.getPasswordFromENC(self.password)
        elif "%%" in self.password:
            password = helpers.evalString(self.password,{"data" : data["flowData"]})
        else:
            password = ""

        client = fortigate.fortigate(host,deviceHostname,user,password=password,port=port,timeout=self.timeout)

        if client.client != None:
            data["eventData"]["remote"]={"client" : client}
            return {"result" : True, "rc" : 0, "msg" : "Connection successful"}
        else:
            return {"result" : False, "rc" : 403, "msg" : "Connection failed - {0}".format(client.error)}

    def setAttribute(self,attr,value,sessionData=None):
        if attr == "password" and not value.startswith("ENC ") and not re.match(".*%%.*%%",value):
            self.password = "ENC {0}".format(auth.getENCFromPassword(value))
            return True
        return super(_remoteConnectFortigate, self).setAttribute(attr,value,sessionData=sessionData)

class _remoteConnectCisco(action._action):
    host = str()
    port = str()
    deviceHostname = str()
    ssh_username = str()
    ssh_password = str()
    enable_password = str()
    timeout = 5

    def doAction(self,data):
        host = helpers.evalString(self.host,{"data" : data["flowData"]})
        port = helpers.evalString(self.port,{"data" : data["flowData"]})
        if not port:
            port = 22
        deviceHostname = helpers.evalString(self.deviceHostname,{"data" : data["flowData"]})
        ssh_username = helpers.evalString(self.ssh_username,{"data" : data["flowData"]})
        if self.ssh_password.startswith("ENC"):
            ssh_password = auth.getPasswordFromENC(self.ssh_password)
        elif "%%" in self.ssh_password:
            ssh_password = helpers.evalString(self.ssh_password,{"data" : data["flowData"]})
        else:
            ssh_password = ""
        if self.enable_password.startswith("ENC"):
            enable_password = auth.getPasswordFromENC(self.enable_password)
        elif "%%" in self.enable_password:
            enable_password = helpers.evalString(self.enable_password,{"data" : data["flowData"]})
        else:
            enable_password = ""

        client = cisco.cisco(host,deviceHostname,ssh_username,ssh_password,enable_password,port,self.timeout)

        if client.client != None:
            data["eventData"]["remote"]={"client" : client}
            return {"result" : True, "rc" : 0, "msg" : "Connection successful"}
        else:
            return {"result" : False, "rc" : 403, "msg" : "Connection failed - {0}".format(client.error)}

    def setAttribute(self,attr,value,sessionData=None):
        if attr == "ssh_password" and not value.startswith("ENC ") and not re.match(".*%%.*%%",value):
            self.ssh_password = "ENC {0}".format(auth.getENCFromPassword(value))
            return True
        if attr == "enable_password" and not value.startswith("ENC ") and not re.match(".*%%.*%%",value):
            self.enable_password = "ENC {0}".format(auth.getENCFromPassword(value))
            return True
        return super(_remoteConnectCisco, self).setAttribute(attr,value,sessionData=sessionData)

class _remoteDisconnect(action._action):
    def doAction(self,data):
        try:
            client = data["eventData"]["remote"]["client"]
        except KeyError:
            client = None
        if client:
            client.disconnect()
        return {"result" : True, "rc" : 0, "msg" : "Connection disconnected"}

class _remoteCommand(action._action):
    command = str()
    arguments = list()
    elevate = bool()
    runAs = str()
    timeout = 60

    def doAction(self,data):
        command = helpers.evalString(self.command,{"data" : data["flowData"]})
        arguments = helpers.evalList(self.arguments,{"data" : data["flowData"]})
        try:
            client = data["eventData"]["remote"]["client"]
        except KeyError:
            client = None
        if client:
            exitCode, output, errors = client.command(command,args=arguments,elevate=self.elevate,runAs=self.runAs,timeout=self.timeout)
            
            if exitCode != None:
                return {"result" : True, "rc" : exitCode, "msg" : "Command succesfull", "data" : output, "errors" : errors}
            else:
                return {"result" : False, "rc" : 255, "msg" : client.error, "data" : output, "errors" : errors}
        else:
            return {"result" : False, "rc" : 403, "msg" : "No connection found"}

class _remoteMultiCommand(action._action):
    commands = str()
    elevate = bool()
    runAs = str()
    timeout = 60
    exitOnFailure = True

    def doAction(self,data):
        commandResults = []
        commands = helpers.evalString(self.commands,{"data" : data["flowData"]})
        try:
            client = data["eventData"]["remote"]["client"]
        except KeyError:
            client = None
        if client:
            if "\n" in commands:
                commands = commands.split("\n")
            else:
                commands = [commands]
            for command in commands:
                args = []
                if " " in command:
                    args = command.split(" ")[1:]
                    command = command.split(" ")[0]
                exitCode, output, errors = client.command(command,args=args,elevate=self.elevate,runAs=self.runAs,timeout=self.timeout)
                if exitCode != None:
                    commandResults.append({"result" : True, "rc" : exitCode, "msg" : "Command succesfull", "data" : output, "command":"{0} {1}".format(command," ".join(args)), "errors" : errors})
                else:
                    if self.exitOnFailure:
                        commandResults.append({"result" : False, "rc" : 255, "msg" : client.error, "data" : output, "errors" : errors, "command":"{0} {1}".format(command," ".join(args))})
                        return {"result" : False, "rc" : 255, "msg" : client.error, "commands" : commandResults, "errors" : errors}
                    else:
                        commandResults.append({"result" : False, "rc" : 255, "msg" : client.error, "data" : output, "errors" : errors, "command":"{0} {1}".format(command," ".join(args))})

            return {"result" : True, "rc" : 0, "msg" : "All commands ran", "commands" : commandResults, "errors" : ""}
            
        else:
            return {"result" : False, "rc" : 403, "msg" : "No connection found"}

class _remoteReboot(action._action):
    timeout = int()

    def doAction(self,data):
        try:
            client = data["eventData"]["remote"]["client"]
        except KeyError:
            client = None
        if client:
            timeout = 60
            if self.timeout > 0:
                timeout = self.timeout
            result = client.reboot(timeout)
            if result:
                return {"result" : True, "rc" : 0, "msg" : "Reboot successful"}
            else:
                return {"result" : False, "rc" : 255, "msg" : "Reboot failed"}
        else:
            return {"result" : False, "rc" : 403, "msg" : "No connection found"}

class _remoteDownload(action._action):
    remoteFile = str()
    localFile = str()
    createMissingFolders = bool()
    useStorage = bool()

    def doAction(self,data):
        remoteFile = helpers.evalString(self.remoteFile,{"data" : data["flowData"]})
        localFile = helpers.evalString(self.localFile,{"data" : data["flowData"]})

        if self.useStorage:
            try:
                localFileClass = jimi.storage._storage().getAsClass(query={ "fileData" : localFile, "systemStorage" : True, "source" : "remoteDownload" })[0]
            except:
                localFileClass = jimi.storage._storage()
                localFileClass.new(self.acl,"remoteDownload",localFile,True)
            localFile = localFileClass.getFullFilePath()

        client = None
        if "remote" in data["eventData"]:
            if "client" in data["eventData"]["remote"]:
                client = data["eventData"]["remote"]["client"]
        if client:
            if client.download(remoteFile,localFile,self.createMissingFolders):
                if self.useStorage:
                    localFileClass.calculateHash()
                    return {"result" : True, "rc" : 0, "msg" : "File transfered successful", "storage" : { "fileHash" : localFileClass.fileHash, "_id" : localFileClass._id } }
                return {"result" : True, "rc" : 0, "msg" : "File transfered successful"}

        return {"result" : False, "rc" : 403, "msg" : "File transfer failed - {0}".format(client.error)}

class _remoteUpload(action._action):
    remoteFile = str()
    localFile = str()
    useStorage = bool()

    def doAction(self,data):
        remoteFile = helpers.evalString(self.remoteFile,{"data" : data["flowData"]})
        localFile = helpers.evalString(self.localFile,{"data" : data["flowData"]})

        if self.useStorage:
            try:
                localFilePath = jimi.storage._storage().getAsClass(id=localFile)[0].getLocalFilePath()
                if not localFilePath:
                    raise
                localFile = localFilePath
            except:
                return {"result" : False, "rc" : 404, "msg" : "Local file not found within storage store. storageID={0}".format(localFile)}

        try:
            client = data["eventData"]["remote"]["client"]
        except KeyError:
            client = None
        if client:
            if client.upload(localFile,remoteFile):
                return {"result" : True, "rc" : 0, "msg" : "File transfered successful"}
        return {"result" : False, "rc" : 403, "msg" : "File transfer failed - {0}".format(client.error)}
