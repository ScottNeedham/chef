#15/08/2016
#To change the cwebs version being updated, update the value in the
#remote_directory guard.

ip=node["ipaddress"].split(".")
octet=ip[2]+"889"


template '/etc/cwebs.conf' do
	source 'cwebsconf.erb'
	mode '755'
	variables( :a => node["ipaddress"], :b => octet)
end
Chef::Log.info(cwebsversion2(node["ipaddress"],octet,"1.0.9"))
remote_directory '/cwebs/cwebs' do
	purge true
	source 'cwebs.1.0.9'
	owner 'root'
	group 'root'
	mode '0755'
	action :create	
	notifies :run, 'bash[restartsupervisord]',:delayed
	notifies :create, 'link[/cwebs/cwebs/config/local_settings.py]',:immediately
	not_if do cwebsversion2(node["ipaddress"],octet,"1.0.9") end 

#	not_if { File.readlines('/cwebs/cwebs/build/build.py').grep(/1.0.9/).size > 0}
end

template '/etc/supervisor/conf.d/cwebs.conf' do
	source 'supervisorcwebs.erb'
	mode '644'
end

bash 'restartsupervisord' do
	cwd '/etc/init.d'
	code <<-EOH
	/etc/init.d/supervisord restart
	EOH
	action :nothing
end

link '/cwebs/cwebs/config/local_settings.py' do
	to '/etc/cwebs.conf'
	action :nothing
end
