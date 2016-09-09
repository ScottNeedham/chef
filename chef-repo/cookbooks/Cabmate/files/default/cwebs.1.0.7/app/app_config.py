from gevent import monkey; monkey.patch_all()
import gevent 
import datetime
from bottle import Bottle, view, template, redirect, request, response, static_file, run, abort, route
import json
import sys
import time
import zqqwrap
import smalldb
import socketcli
import socket
import thread
import cwebsconf2 as Config
import itcli
import format_field
import dblayer
import validpr
import driver
import vehicle
import msgconf
import cabmsg
import struct
import sanity_check
import scap


import api_funcs, fare_funcs

'''

app_routing_rules = {
    
    [ '/cwebs/version/', ['GET'], api_funcs.get_cwebs_version  ],

    [ '/cwebs/hostinfo/', ['GET'], api_funcs.get_cwebs_hostinfo ] ,


    { '/device/clear_emergency/', ['POST'], callback= funcs.clear_device_emergency 
    { '/message/send_fleet_msg/', method='POST', callback= funcs.fleet_send_msg)

    { '/message/send_vehicle_msg/', method='POST' , callback= funcs.vehicle_send_msg)
    { '/message/send_driver_msg/',  method='POST' , callback=funcs.driver_send_msg)
    { '/dispatcher/queues/', method='POST' , callback= funcs.dispatch_queues)

    { '/driver/action/',  method='POST' , callback= funcs.driver_action)
    { '/vehicle/action/', method='POST' , callback= funcs.vehicle_action)
    { '/device/sendmsg/',  method='POST' , callback=funcs.device_sendmsg)


    # fare_funcs.py
    { '/dispatcher/cancel_book_order/',  method='POST' , callback=fare_funcs.dispatch_cancel_book_order)
    { '/dispatcher/save_book_order/',  method='POST' , callback=fare_funcs.dispatch_save_book_order)
    { '/dispatcher/modify_book_order/',  method='POST' , callback=fare_funcs.dispatch_modify_book_order)


}
'''

if __name__ == "__main__":


    sockcli = socketcli.sClient(Config.SocketServerHost, Config.SocketServerPort, thread.allocate_lock())

    th1 = gevent.spawn(sockcli.receive_server_response)

    myapp = Bottle()

    myapp.route('/cwebs/version/', ['GET', 'POST'], api_funcs._get_version )
    myapp.route('/cwebs/hostinfo/', ['GET', 'POST'], api_funcs._get_hostinfo)

    myapp.route('/device/clear_emergency/', ['POST'], api_funcs._clear_device_emergency)
    myapp.route('/message/send_fleet_msg/', ['POST'], api_funcs._fleet_send_msg)

    myapp.route('/fleet/action/', ['POST'], api_funcs._modify_fleet)


    run(myapp, host=Config.BOTTLE_IP, port=Config.BOTTLE_PORT, reloader=Config.BOTTLE_AUTO_RELOAD, debug=Config.BOTTLE_DEBUG, server=Config.BOTTLE_SERVER) 

    try:
        sockcli.sockobj.shutdown(socket.SHUT_RDWR)
        sockcli.sockobj.close()   
    except Exception as e:
        pass
