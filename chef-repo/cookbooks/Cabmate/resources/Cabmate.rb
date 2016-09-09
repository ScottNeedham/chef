resource_name :cabmate
#Usage: msgsender [ -f filename [ filename ... ] ]
#                 [ -s dstid srcid srcmch scndid mtype priority wait textdata ]
action :rsp do
	bash 'rsp' do
	cwd '/mkc/bin'
	code <<-EOH
		/mkc/bin/msgsender -s 7 0 0 0 30 1 0 0
		/mkc/bin/msgsender -s 9 0 0 0 30 1 0 0
		/mkc/bin/msgsender -s 10 0 0 0 30 1 0 0
		/mkc/bin/msgsender -s 65 0 0 0 30 1 0 0
		/mkc/bin/msgsender -s 5 0 0 0 30 1 0 0
		/mkc/bin/msgsender -s 4 0 0 0 30 1 0 0
		/mkc/bin/msgsender -s 3 0 0 0 30 1 0 0
		/mkc/bin/msgsender -s 2 0 0 0 30 1 0 0
	EOH
	end
end








