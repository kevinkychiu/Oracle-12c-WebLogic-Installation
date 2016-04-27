# Oracle-12c-WebLogic-Installation

<h4>infrastructure.rsp</h4>
<p>WebLogic installation repsonse file.</p>
<ul>
	<li>Update ORACLE_HOME to your oralce home location.</li>
</ul>

<h4>soa.rsp</h4>
<p>WebLogic SOA installation repsonse file.</p>
<ul>
	<li>Update ORACLE_HOME to your oralce home location.</li>
</ul>


<h4>oraInst.loc</h4>
<p>oraInventory configuration.</p>
<ul>
	<li>Configure the Oracle inventory location 'inventory_loc'.</li>
	<li>Configure the Oracle installation group 'inst_group'.</li>
</ul>

<h4>rcuCreateRepository.properties</h4>
<p>Response file for Repository Creation Utility.</p>
<ul>
	<li>'connectString' - Database connection string</li>
	<li>'dbUser' - Database user to create the repository.</li>
	<li>'schemaPrefix' - The SOA schema prefix.</li>
	<li>'SOA_PROFILE_TYPE' - Configure the profile size (SMALL/MED/LARGE).</li>
</ul>
<p>To drop a repostiory, please use the same response file with operation=dropRepository.</p>

<h4>soa_domain_1221.py</h4>
<p>Sample SOA_DOMAIN python script for Oracle SOA 12.2.1.0.0 and generate the WLST python script to start/stop WebLogic.</p>
<ul>
	<li>start - $DOMAIN_HOME/bin/wlst.sh start</li>
	<li>stop - $DOMAIN_HOME/bin/wlst.sh stop</li>
</ul>
