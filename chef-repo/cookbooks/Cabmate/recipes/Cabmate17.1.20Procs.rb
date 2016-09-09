#
# Cookbook Name:: webserver
# Recipe:: Cabmate17.1.20Procs.rb


directory "/mkc/ngateproto" do
  recursive true
end

cookbook_file "/mkc/ngateproto/ngateproto.17.1.86" do
	source "ngateproto.17.1.86"
	mode "755"
	action :create_if_missing
end

link '/mkc/ngateproto/ngateproto' do
	to '/mkc/ngateproto/ngateproto.17.1.86'
	notifies :rsp, 'cabmate[rsp]',:immediately
end

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

cookbook_file "/mkc/disp_mgr/disp_mgr.17.1.71.128" do
        source "disp_mgr.17.1.71.128"
        mode "755"
	action :create_if_missing

end

link '/mkc/disp_mgr/disp_mgr' do
	to '/mkc/disp_mgr/disp_mgr.17.1.71.128'
	notifies :rsp, 'cabmate[rsp]',:immediately
end

directory "/mkc/tfcserv" do
  recursive true
end

cookbook_file "/mkc/tfcserv/tfcserv.17.1.65" do
        source "tfcserv.17.1.65"
        mode "755"
	action :create_if_missing
end

link '/mkc/tfcserv/tfcserv' do
	to '/mkc/tfcserv/tfcserv.17.1.65'
	notifies :rsp, 'cabmate[rsp]',:immediately
end

cookbook_file "/mkc/bin/vtrack.17.1.9" do
        source "vtrack.17.1.9"
        mode "755"
end

link '/mkc/bin/vtrack' do
        to '/mkc/bin/vtrack.17.1.9'     
end

#idempotence
cabmate 'rsp' do	
	action :nothing
end

#
# Copyright (c) 2016 The Authors, All Rights Reserved.
