#!/usr/bin/env ruby
require 'net/http'
require 'json'
require 'pp'


def cwebsversion(x,y)
return 'http://'+x+ ':' +y+'/cwebs/version/'
#return x +':' +y
end
  
begin
	puts cwebsversion("52.20.159.128","33889")
end