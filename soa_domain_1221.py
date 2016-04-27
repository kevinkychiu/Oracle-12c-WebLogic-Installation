JAVA_HOME      = '/usr/lib/jvm/java-8-oracle'

MW_HOME     = '/home/oracle/Oracle/Middleware/Oracle_Home'
WL_HOME     = MW_HOME + '/wlserver'

DOMAIN      = 'soa_domain'
DOMAIN_PATH = MW_HOME + '/user_projects/domains/' + DOMAIN
APP_PATH    = MW_HOME + '/user_projects/applications/' + DOMAIN

SERVER_ADDRESS = 'All Local Addresses'
LOG_FOLDER     = DOMAIN_PATH + '/servers/'

JSSE_ENABLED     = true
DEVELOPMENT_MODE = false

ADMIN_SERVER       = 'AdminServer'
ADMIN_USER         = 'weblogic'
ADMIN_PASSWORD     = 'welcome1'
ADMIN_SERVER_PORT  = 7001
NODE_MANAGER_PORT  = 5556

ADM_JAVA_ARGUMENTS = '-XX:PermSize=256m -XX:MaxPermSize=512m -Xms1024m -Xmx1532m'
ADM_JAVA_ARGUMENTS = ADM_JAVA_ARGUMENTS + ' -Dweblogic.Stdout=' + LOG_FOLDER + 'AdminServer/logs/AdminServer.out'
ADM_JAVA_ARGUMENTS = ADM_JAVA_ARGUMENTS + ' -Dweblogic.Stderr=' + LOG_FOLDER + 'AdminServer/logs/AdminServer_err.out'
SOA_JAVA_ARGUMENTS = '-XX:PermSize=256m -XX:MaxPermSize=752m -Xms1024m -Xmx1532m '


SOA_REPOS_DBURL          = 'jdbc:oracle:thin:@DB_HOST:DB_PORT/SERVICE_NAME'
SOA_REPOS_DBUSER_PREFIX  = 'DEV'
SOA_REPOS_DBPASSWORD     = 'soa'

MACHINE         = 'soa_machine'
CLUSTER         = 'soa_cluster'
MANAGED_SERVERS = {
  'soa_server1': 7003
}


def createBootPropertiesFile(directoryPath,fileName, username, password):
  serverDir = File(directoryPath)
  bool = serverDir.mkdirs()
  fileNew=open(directoryPath + '/'+fileName, 'w')
  fileNew.write('username=%s\n' % username)
  fileNew.write('password=%s\n' % password)
  fileNew.flush()
  fileNew.close()

def createAdminStartupPropertiesFile(directoryPath, args):
  adminserverDir = File(directoryPath)
  bool = adminserverDir.mkdirs()
  fileNew=open(directoryPath + '/startup.properties', 'w')
  args=args.replace(':','\\:')
  args=args.replace('=','\\=')
  fileNew.write('Arguments=%s\n' % args)
  fileNew.flush()
  fileNew.close()

def changeDatasourceToXA(datasource):
  print 'Change datasource '+datasource
  cd('/')
  cd('/JDBCSystemResource/'+datasource+'/JdbcResource/'+datasource+'/JDBCDriverParams/NO_NAME_0')
  set('DriverName','oracle.jdbc.xa.client.OracleXADataSource')
  set('UseXADataSourceInterface','True') 
  cd('/JDBCSystemResource/'+datasource+'/JdbcResource/'+datasource+'/JDBCDataSourceParams/NO_NAME_0')
  set('GlobalTransactionsProtocol','TwoPhaseCommit')
  cd('/')

def changeManagedServer(server, port, java_arguments):
  cd('/Servers/'+server)
  set('Machine'      , MACHINE)
  set('ListenAddress', SERVER_ADDRESS)
  set('ListenPort'   ,port)
  create(server, 'ServerStart')
  cd('ServerStart/'+server)
  set('Arguments' , java_arguments + ' -Dweblogic.Stdout=' + LOG_FOLDER + server + '/logs/' + server +'.out'
    +' -Dweblogic.Stderr=' + LOG_FOLDER + server + '/logs/' + server + '_err.out')
  set('JavaVendor','Sun')
  set('JavaHome'  , JAVA_HOME)
  cd('/Server/' + server)
  create(server, 'SSL')
  cd('SSL/' + server)
  set('Enabled'                    , 'False')
  set('HostNameVerificationIgnored', 'True')
  set('ListenPort'                 , port + 500)
  if JSSE_ENABLED == true:
    set('JSSEEnabled','True')
  else:
    set('JSSEEnabled','False')  
  cd('/Server/'+server)
  create(server,'Log')
  cd('/Server/'+server+'/Log/'+server)
  set('FileCount'    , 10)
  set('FileMinSize'  , 5000)
  set('RotationType' ,'byTime')
  set('FileTimeSpan' , 24)



print('Start...wls domain with template /opt/oracle/middleware12c/wlserver/common/templates/wls/wls.jar')
selectTemplate("Basic WebLogic Server Domain", "12.2.1")
loadTemplates()


cd('/')

cd('/Servers/AdminServer')
# name of adminserver
set('Name', ADMIN_SERVER)
cd('/Servers/' + ADMIN_SERVER)

# address and port
set('ListenAddress', SERVER_ADDRESS)
set('ListenPort'   , ADMIN_SERVER_PORT)

setOption( "AppDir", APP_PATH )

create(ADMIN_SERVER, 'ServerStart')
cd('ServerStart/' + ADMIN_SERVER)
set('Arguments' , ADM_JAVA_ARGUMENTS)
set('JavaVendor', 'Sun')
set('JavaHome'  , JAVA_HOME)

cd('/Server/' + ADMIN_SERVER)
create(ADMIN_SERVER, 'SSL')
cd('SSL/' + ADMIN_SERVER)
set('Enabled'                    , 'False')
set('HostNameVerificationIgnored', 'True')
set('ListenPort'                 , ADMIN_SERVER_PORT + 1)

if JSSE_ENABLED == true:
  set('JSSEEnabled','True')
else:
  set('JSSEEnabled','False')


cd('/Server/'+ADMIN_SERVER)

create(ADMIN_SERVER,'Log')
cd('/Server/'+ADMIN_SERVER+'/Log/'+ADMIN_SERVER)
set('FileCount'   , 10)
set('FileMinSize' , 5000)
set('RotationType', 'byTime')
set('FileTimeSpan', 24)

print('Set password...')
cd('/')
cd('Security/base_domain/User/weblogic')

# weblogic user name + password
set('Name', ADMIN_USER)
cmo.setPassword(ADMIN_PASSWORD)

if DEVELOPMENT_MODE == true:
  setOption('ServerStartMode', 'dev')
else:
  setOption('ServerStartMode', 'prod')

setOption('JavaHome', JAVA_HOME)

print('write domain...')
# write path + domain name
writeDomain(DOMAIN_PATH)
closeTemplate()


nmPropFileSrc=DOMAIN_PATH + '/nodemanager/nodemanager.properties'
nmPropFileData = ''
nmPropFile =open(nmPropFileSrc, 'r+')
for line in nmPropFile:
  nmPropFileData += line

nmPropFileData=nmPropFileData.replace('ListenPort=5556', 'ListenPort=' + str(NODE_MANAGER_PORT))
nmPropFile =open(nmPropFileSrc, 'w')
nmPropFile.write(nmPropFileData);
nmPropFile.close()

createAdminStartupPropertiesFile(DOMAIN_PATH + '/servers/' + ADMIN_SERVER + '/data/nodemanager', ADM_JAVA_ARGUMENTS)

readDomain(DOMAIN_PATH)

print 'Adding SOA Template'
selectTemplate("Oracle SOA Suite", "12.2.1")
loadTemplates()
# Delete the default soa_server1
delete('soa_server1', 'Server')

es = encrypt(ADMIN_PASSWORD, DOMAIN_PATH)

print('set domain password...') 
cd('/SecurityConfiguration/' + DOMAIN)
set('CredentialEncrypted', es)

print('Set nodemanager password')
set('NodeManagerUsername'         , ADMIN_USER)
set('NodeManagerPasswordEncrypted', es)

cd('/')

setOption( "AppDir", APP_PATH )

dumpStack()

print 'Change datasources'

print 'Change datasource LocalScvTblDataSource'
cd('/JDBCSystemResource/LocalSvcTblDataSource/JdbcResource/LocalSvcTblDataSource/JDBCDriverParams/NO_NAME_0')
set('URL',SOA_REPOS_DBURL)
set('PasswordEncrypted', SOA_REPOS_DBPASSWORD)
cd('Properties/NO_NAME_0/Property/user')
set('Value', SOA_REPOS_DBUSER_PREFIX + '_STB')

print 'Call getDatabaseDefaults which reads the service table'
getDatabaseDefaults()    

changeDatasourceToXA('EDNDataSource')
changeDatasourceToXA('OraSDPMDataSource')
changeDatasourceToXA('SOADataSource')

print('Create machine soa_machine with type UnixMachine')
cd('/')
create(MACHINE, 'UnixMachine')
cd('UnixMachine/' + MACHINE)
create(MACHINE, 'NodeManager')
cd('NodeManager/' + MACHINE)
set('ListenAddress', SERVER_ADDRESS)
set('ListenPort', NODE_MANAGER_PORT)

print 'Change AdminServer'
cd('/Servers/' + ADMIN_SERVER)
set('Machine', MACHINE)

print 'Add server groups WSM-CACHE-SVR WSMPM-MAN-SVR JRF-MAN-SVR to AdminServer'
serverGroup = ["WSM-CACHE-SVR" , "WSMPM-MAN-SVR" , "JRF-MAN-SVR"]
setServerGroups(ADMIN_SERVER, serverGroup)


print 'Create soa_cluster'
cd('/')
create(CLUSTER, 'Cluster')


serverGroup = ["SOA-MGD-SVRS"]
for serverName, port in MANAGED_SERVERS.items():
  print('')
  print('Creating Managed Server - %s#%d' % (serverName, port))
  cd('/')
  create(serverName, 'Server')
  cd('Server/' + serverName)
  set('ListenAddress', SERVER_ADDRESS)
  set('ListenPort', port)
  changeManagedServer(serverName, port, SOA_JAVA_ARGUMENTS)
  createBootPropertiesFile(DOMAIN_PATH + '/servers/' + serverName + '/security', 'boot.properties', ADMIN_USER, ADMIN_PASSWORD)
  setServerGroups(serverName, serverGroup)


cd('/')
assign('Server', ','.join(MANAGED_SERVERS.keys()), 'Cluster', CLUSTER)


updateDomain()
closeDomain();

createBootPropertiesFile(DOMAIN_PATH+'/servers/'+ADMIN_SERVER+'/security','boot.properties',ADMIN_USER,ADMIN_PASSWORD)
createBootPropertiesFile(DOMAIN_PATH+'/config/nodemanager','nm_password.properties',ADMIN_USER,ADMIN_PASSWORD)


#
# Create user.secure and key.secure files for WLST.
#
print '>>'
print '>> START NODE MANAGER'
print '>>'
NM_HOME=DOMAIN_PATH + '/nodemanager'
startNodeManager(verbose='true', NodeManagerHome=NM_HOME)
print ' '
print '>>'
print '>> CONNECT TO NODE MANAGER'
print '>>'
nmConnect(username=ADMIN_USER, password=ADMIN_PASSWORD, host='localhost', port=str(NODE_MANAGER_PORT), domainName=DOMAIN, domainDir=DOMAIN_PATH, nmType='ssl')
print ' '
print '>>'
print '>> CREATE USER CONFIG'
print '>>'
storeUserConfig(DOMAIN_PATH + '/bin/' + DOMAIN + '_user.secure', DOMAIN_PATH + '/bin/' + DOMAIN + '_key.secure', nm='true')
print ' '
print '>>'
print '>> STOP NODE MANAGER'
print '>>'
stopNodeManager()



# Create wlst.sh file
WLST_SH_FILE=DOMAIN_PATH+'/bin/wlst.sh'
wlstShFile=open(WLST_SH_FILE, 'w')
wlstShFile.write("#!/bin/sh\n")
wlstShFile.write("\n")
wlstShFile.write("ERROR_MSG=\"Usage wlst.sh [start|stop]\"" + "\n")
wlstShFile.write("\n")
wlstShFile.write("if [ $# -eq 0 ]; then" + "\n")
wlstShFile.write("    echo $ERROR_MSG" + "\n")
wlstShFile.write("    exit 1" + "\n")
wlstShFile.write("fi" + "\n")
wlstShFile.write("\n")
wlstShFile.write("if [ $1 != \"start\" ] && [ $1 != \"stop\" ]; then" + "\n")
wlstShFile.write("    echo $ERROR_MSG" + "\n")
wlstShFile.write("    exit 2" + "\n")
wlstShFile.write("fi" + "\n")
wlstShFile.write("\n")
wlstShFile.write("MW_HOME=" + MW_HOME + "\n");
wlstShFile.write("WL_HOME=" + WL_HOME + "\n");
wlstShFile.write("\n")
wlstShFile.write("WLS_ENV=`$WL_HOME/server/bin/setWLSEnv.sh`" + "\n");
wlstShFile.write("WLS_ENV=`echo $WLS_ENV | sed 's/: PATH.*//'`" + "\n");
wlstShFile.write("CLASSPATH=`echo $WLS_ENV | sed 's/CLASSPATH=//'`" + "\n");
wlstShFile.write("\n")
wlstShFile.write("JAVA_HOME=" + JAVA_HOME + "\n")
wlstShFile.write("JAVA=$JAVA_HOME/jre/bin/java" + "\n")
wlstShFile.write("\n")
wlstShFile.write("$JAVA -version" + "\n")
wlstShFile.write("\n")
#wlstShFile.write("$JAVA -cp $CLASSPATH $JAVA_OPTIONS weblogic.WLST $1.py" + "\n")
wlstShFile.write("$MW_HOME/oracle_common/common/bin/wlst.sh $1.py" + "\n")
wlstShFile.close()
os.system("chmod 750 " + WLST_SH_FILE);


USER_CONFIG_FILE = DOMAIN + '_user.secure'
USER_KEY_FILE    = DOMAIN + '_key.secure'

START_PY_FILE=DOMAIN_PATH+'/bin/start.py'
startPyFile=open(START_PY_FILE, 'w')
startPyFile.write("DOMAIN_HOME       = '" + DOMAIN_PATH + "'" + "\n")
startPyFile.write("NM_HOME           = '" + DOMAIN_PATH + "/nodemanager'" + "\n")
startPyFile.write("USER_CONFIG_FILE  = '" + USER_CONFIG_FILE + "'" + "\n")
startPyFile.write("USER_KEY_FILE     = '" + USER_KEY_FILE + "'" + "\n")
startPyFile.write("HOST              = 'localhost'" + "\n")
startPyFile.write("NODE_MANAGER_PORT = '" + str(NODE_MANAGER_PORT) + "'" + "\n")
startPyFile.write("DOMAIN_NAME       = '" + DOMAIN + "'" + "\n")
startPyFile.write("\n")
startPyFile.write("print 'DOMAIN_HOME: ' + DOMAIN_HOME" + "\n")
startPyFile.write("print 'NM_HOME    : ' + NM_HOME" + "\n")
startPyFile.write("print ' '" + "\n")
startPyFile.write("\n")
startPyFile.write("print '>> START NODE MANAGER'" + "\n")
startPyFile.write("startNodeManager(verbose='false', NodeManagerHome=NM_HOME)" + "\n")
startPyFile.write("print ' '" + "\n")
startPyFile.write("\n")
startPyFile.write("print '>> CONNECT TO NODE MANAGER'" + "\n")
startPyFile.write("nmConnect(userConfigFile=USER_CONFIG_FILE, userKeyFile=USER_KEY_FILE"
  + ", host=HOST, port=NODE_MANAGER_PORT, domainName=DOMAIN_NAME, domainDir=DOMAIN_HOME, nmType='ssl')" + "\n")
startPyFile.write("print ' '" + "\n")
startPyFile.write("\n")
startPyFile.write("print '>> START ADMIN SERVER'" + "\n")
startPyFile.write("nmStart('" + ADMIN_SERVER + "')" + "\n")
startPyFile.write("nmServerStatus('" + ADMIN_SERVER + "')" + "\n")
startPyFile.write("print ' '" + "\n")
startPyFile.write("\n")
startPyFile.write("print '>> CONNECT TO ADMIN SERVER'" + "\n")
startPyFile.write("connect(userConfigFile=USER_CONFIG_FILE, userKeyFile=USER_KEY_FILE, url='t3://localhost:" + str(ADMIN_SERVER_PORT) + "')" + "\n")
startPyFile.write("\n")
startPyFile.write("print '>> START MANAGER SERVER(s)'" + "\n")
for serverName, port in MANAGED_SERVERS.items():
  startPyFile.write("start('" + serverName + "', 'Server')" + "\n")

startPyFile.write("print ' '" + "\n")
startPyFile.write("\n")
startPyFile.write("exit()" + "\n")
startPyFile.close()
os.system("chmod 650 " + START_PY_FILE);


STOP_PY_FILE=DOMAIN_PATH+'/bin/stop.py'
stopPyFile=open(STOP_PY_FILE, 'w')
stopPyFile.write("DOMAIN_HOME='" + DOMAIN_PATH + "'" + "\n")
stopPyFile.write("NM_HOME='" + DOMAIN_PATH + "/nodemanager'" + "\n")
stopPyFile.write("USER_CONFIG_FILE  = '" + USER_CONFIG_FILE + "'" + "\n")
stopPyFile.write("USER_KEY_FILE     = '" + USER_KEY_FILE + "'" + "\n")
stopPyFile.write("HOST              = 'localhost'" + "\n")
stopPyFile.write("NODE_MANAGER_PORT = '" + str(NODE_MANAGER_PORT) + "'" + "\n")
stopPyFile.write("DOMAIN_NAME       = '" + DOMAIN + "'" + "\n")
stopPyFile.write("\n")
stopPyFile.write("print 'DOMAIN_HOME: ' + DOMAIN_HOME" + "\n")
stopPyFile.write("print 'NM_HOME    : ' + NM_HOME" + "\n")
stopPyFile.write("print ' '" + "\n")
stopPyFile.write("\n")
stopPyFile.write("print '>> CONNECT TO NODE MANAGER'" + "\n")
stopPyFile.write("nmConnect(userConfigFile=USER_CONFIG_FILE, userKeyFile=USER_KEY_FILE"
  + ", host=HOST, port=NODE_MANAGER_PORT, domainName=DOMAIN_NAME, domainDir=DOMAIN_HOME, nmType='ssl')" + "\n")
stopPyFile.write("print ' '" + "\n")
stopPyFile.write("\n")
stopPyFile.write("nmServerStatus('" + ADMIN_SERVER + "')" + "\n")
stopPyFile.write("\n")
stopPyFile.write("print '>> CONNECT TO ADMIN SERVER'" + "\n")
stopPyFile.write("connect(userConfigFile=USER_CONFIG_FILE, userKeyFile=USER_KEY_FILE, url='t3://localhost:" + str(ADMIN_SERVER_PORT) + "')" + "\n")
stopPyFile.write("print ' '" + "\n")
stopPyFile.write("\n")
stopPyFile.write("print '>> SHUTDOWN MANAGER SERVER(s)'" + "\n")
for serverName, port in MANAGED_SERVERS.items():
  stopPyFile.write("shutdown(name='" + serverName + "', entityType='Server', ignoreSessions='true', timeOut=180, force='false')" + "\n")

stopPyFile.write("print ' '" + "\n")
stopPyFile.write("\n")
stopPyFile.write("print '>> SHUTDOWN ADMIN SERVER'" + "\n")
stopPyFile.write("shutdown(name='" + ADMIN_SERVER + "', entityType='Server', ignoreSessions='true', timeOut=180, force='false')" + "\n")
stopPyFile.write("print ' '" + "\n")
stopPyFile.write("\n")
stopPyFile.write("print '>> SHUTDOWN NODE MANAGER'" + "\n")
stopPyFile.write("stopNodeManager()" + "\n")
stopPyFile.write("print ' '" + "\n")
stopPyFile.write("\n")
stopPyFile.close()
os.system("chmod 650 " + STOP_PY_FILE)


print('Exiting...')
exit()

