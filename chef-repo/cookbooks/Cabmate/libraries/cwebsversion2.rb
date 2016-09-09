#!/usr/bin/env ruby -w
require 'net/http'
require 'json'
require 'pp'


def cwebsversion2(x,y,z)
  
  begin 
 	url=('http://'+x+ ':' +y+'/cwebs/version/')
    uri = URI(url)
	Net::HTTP.start(uri.host, uri.port) do |http|
	request = Net::HTTP::Get.new uri
  	response = http.request request
  	json_hash = JSON.parse(response.body)
	version = json_hash["result"]["version"]
		
		if version == z
			return true
		else
			return false  
		end
  	
  end
  rescue => e
    return false    
  end 
end 