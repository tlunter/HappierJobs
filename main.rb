require 'excon'
require 'json'

def get_page(url)
  res = Excon.get(url)
  json = JSON.parse(res.body)

  puts json["goal"]

  get_direction(json)
end

def get_direction(json)
  ["east", "south", "north", "west"].each do |dir|
    if json["goal"].include?(dir) && json.has_key?(dir)
      puts "Getting #{json[dir]}"
      get_page(json[dir])
      return
    end
  end
  puts "What now?"
end

get_page('http://jobs.happier.com/1111')
