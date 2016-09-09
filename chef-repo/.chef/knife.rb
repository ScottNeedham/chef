# See https://docs.chef.io/aws_marketplace.html/config_rb_knife.html for more information on knife configuration options

current_dir = File.dirname(__FILE__)
log_level                :info
log_location             STDOUT
node_name                "sneedham"
client_key               "#{current_dir}/sneedham.pem"
validation_client_name   "cmtgroup-validator"
validation_key           "#{current_dir}/cmtgroup-validator.pem"
chef_server_url          "https://chef.drivelinq.com/organizations/cmtgroup"
cookbook_path            ["#{current_dir}/../cookbooks"]
