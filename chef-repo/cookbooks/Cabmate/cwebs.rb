Chef::Log.info("#{node["name"]} has IP address #{node["ipaddress"]}")
ip=node["ipaddress"].split(".")
#ip="10.11.12.13".split(".")
octet=ip[2]+"889"
Chef::Log.info(octet)

template '/etc/cwebs.conf' do
	source 'cwebs.erb'
	mode '755'
	variable( :a => node["ipaddress"], :b => octet)
end


