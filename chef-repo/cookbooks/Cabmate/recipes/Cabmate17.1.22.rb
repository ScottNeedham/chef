#
# Cookbook Name:: webserver
# Recipe:: Cabmate17.1.21Procs.rb


directory "/mkc/base_in" do
  recursive true
end

cookbook_file "/mkc/base_in/base_in.17.1.11" do
        source "base_in.17.1.11"
        mode "755"
	action :create_if_missing
end

link '/mkc/base_in/base_in' do
	to '/mkc/base_in/base_in.17.1.11'
	notifies :rsp, 'cabmate[rsp]',:immediately
end

directory "/mkc/disp_mgr" do
  recursive true
end

cookbook_file "/mkc/disp_mgr/disp_mgr.17.1.80.128" do
        source "disp_mgr.17.1.80.128"
        mode "755"
	action :create_if_missing
end

link '/mkc/disp_mgr/disp_mgr' do
	to '/mkc/disp_mgr/disp_mgr.17.1.80.128'
	notifies :rsp, 'cabmate[rsp]',:immediately
end

directory "/mkc/tfcserv" do
  recursive true
end

cookbook_file "/mkc/tfcserv/tfcserv.17.1.81" do
        source "tfcserv.17.1.81"
        mode "755"
	action :create_if_missing
end

link '/mkc/tfcserv/tfcserv' do
	to '/mkc/tfcserv/tfcserv.17.1.81'
	notifies :rsp, 'cabmate[rsp]',:immediately
end

cookbook_file "/mkc/bin/vtrack.17.1.9" do
        source "vtrack.17.1.9"
        mode "755"
end

link '/mkc/bin/vtrack' do
        to '/mkc/bin/vtrack.17.1.9'     
end

directory "/mkc/cabmatesrv" do
  recursive true
end

cookbook_file "/mkc/cabmatesrv/cabmatesrv.17.1.50" do
	source "cabmatesrv.17.1.50"
	mode "755"
	action :create_if_missing
end

link '/mkc/cabmatesrv/cabmatesrv' do
	to '/mkc/cabmatesrv/cabmatesrv.17.1.50'
	notifies :rsp, 'cabmate[rsp]',:immediately
end

directory "/mkc/cc_proc" do
  recursive true
end

cookbook_file "/mkc/cc_proc/cc_proc.17.1.5" do
	source "cc_proc.17.1.5"
	mode "755"
	action :create_if_missing
end

link '/mkc/cc_proc/cc_proc' do
	to '/mkc/cc_proc/cc_proc.17.1.5'
	notifies :rsp, 'cabmate[rsp]',:immediately
end


directory "/mkc/itaxisim" do
  recursive true
end

cookbook_file "/mkc/itaxisim/itaxisim.17.1.2" do
	source "itaxisim.17.1.2"
	mode "755"
	action :create_if_missing
end

link '/mkc/itaxisim/itaxisim' do
	to '/mkc/itaxisim/itaxisim.17.1.2'
	notifies :rsp, 'cabmate[rsp]',:immediately
end

directory "/mkc/itaxissrv" do
  recursive true
end

cookbook_file "/mkc/itaxisrv/taxisrv.17.1.34" do
	source "itaxisrv.17.1.34"
	mode "755"
	action :create_if_missing
end

link '/mkc/itaxisrv/itaxisrv' do
	to '/mkc/itaxisrv/taxisrv.17.1.34'
	notifies :rsp, 'cabmate[rsp]',:immediately
end

directory "/mkc/itaxissrv1" do
  recursive true
end

cookbook_file "/mkc/itaxisrv1/itaxisrv1.17.1.33" do
	source "itaxisrv1.17.1.33"
	mode "755"
	action :create_if_missing
end

link '/mkc/itaxisrv1/itaxisrv1' do
	to '/mkc/itaxisrv1/itaxisrv1.17.1.33'
	notifies :rsp, 'cabmate[rsp]',:immediately
end

directory "/mkc/ngateproto" do
  recursive true
end

cookbook_file "/mkc/ngateproto/ngateproto.17.1.104" do
	source "ngateproto.17.1.104"
	mode "755"
	action :create_if_missing
end

link '/mkc/ngateproto/ngateproto' do
	to '/mkc/ngateproto/ngateproto.17.1.104'
	notifies :rsp, 'cabmate[rsp]',:immediately
end

directory "/mkc/timemgr" do
  recursive true
end

cookbook_file "/mkc/timemgr/timemgr.17.1.24.128" do
	source "timemgr.17.1.24.128"
	mode "755"
	action :create_if_missing
end

link '/mkc/timemgr/timemgr' do
	to '/mkc/timemgr/timemgr.17.1.24.128'
	notifies :rsp, 'cabmate[rsp]',:immediately
end

directory "/mkc/mycabmatesrv" do
  recursive true
end

cookbook_file "/mkc/mycabmatesrv/mycabmatesrv.17.1.6" do
	source "mycabmatesrv.17.1.6"
	mode "755"
	action :create_if_missing
end

link '/mkc/mycabmatesrv/mycabmatesrv' do
	to '/mkc/mycabmatesrv/mycabmatesrv.17.1.6'
	notifies :rsp, 'cabmate[rsp]',:immediately
end

cookbook_file "/mkc/bin/ccrec.17.1.5" do
	source "ccrec.17.1.5"
	mode "755"
	action :create_if_missing
end

link '/mkc/bin/ccrec' do
	to '/mkc/bin/ccrec.17.1.5'
	notifies :rsp, 'cabmate[rsp]',:immediately
end

cookbook_file "/mkc/bin/wccrecZero.17.1.5" do
	source "wccrecZero.17.1.5"
	mode "755"
	action :create_if_missing
end

link '/mkc/bin/wccrecZero' do
	to '/mkc/bin/wccrecZero.17.1.5'
	notifies :rsp, 'cabmate[rsp]',:immediately
end

cookbook_file "/mkc/bin/scapadd.17.1.24" do
	source "scapadd.17.1.24"
	mode "755"
	action :create_if_missing
	
end

link '/mkc/bin/scapadd.17.1.24' do
	to '/mkc/bin/scapadd'
	notifies :run, 'bash[restartsupervisord]',:delayed	
end

cookbook_file "/mkc/bin/farerr.17.0.0" do
	source "farerr.17.0.0"
	mode "755"
	action :create_if_missing
	
end

link '/mkc/bin/farerr.17.0.0' do
	to '/mkc/bin/farerr'
	notifies :run, 'bash[restartsupervisord]',:delayed	
end

cookbook_file "/mkc/bin/getzone.17.0.0" do
	source "getzone.17.0.0"
	mode "755"
	action :create_if_missing
	
end

link '/mkc/bin/getzone.17.0.0' do
	to '/mkc/bin/getzone'
	notifies :run, 'bash[restartsupervisord]',:delayed	
end
#idempotence
cabmate 'rsp' do	
	action :nothing
end

cookbook_file "/mkc/bin/gridexam.17.0.0" do
	source "gridexam.17.0.0"
	mode "755"
	action :create_if_missing
	
end

link '/mkc/bin/gridexam.17.0.0' do
	to '/mkc/bin/gridexam'
	notifies :run, 'bash[restartsupervisord]',:delayed	
end

cookbook_file "/mkc/bin/rr.17.1.12" do
	source "rr.17.1.12"
	mode "755"
	action :create_if_missing
	
end

link '/mkc/bin/rr.17.1.12' do
	to '/mkc/bin/rr'
	notifies :run, 'bash[restartsupervisord]',:delayed	
end

cookbook_file "/mkc/bin/smemrr.17.0.0" do
	source "smemrr.17.0.0"
	mode "755"
	action :create_if_missing
	
end

link '/mkc/bin/smemrr.17.0.0' do
	to '/mkc/bin/smemrr'
	notifies :run, 'bash[restartsupervisord]',:delayed	
end

#idempotence
cabmate 'rsp' do	
	action :nothing
end

bash 'run_scapadd' do
	cwd '/mkc/bin'
	code <<-EOF
	/mkc/bin/scapadd
	EOF
	action :nothing
end


