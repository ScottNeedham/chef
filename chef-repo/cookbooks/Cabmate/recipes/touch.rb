#idempotence test
execute 'touch' do
	command 'touch /mkc/CabmateVersion.17.1.20'
	action:nothing
end
