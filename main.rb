require 'excon'
require 'json'
require 'pry'

def get_page(url)
  res = Excon.get(url)
  JSON.parse(res.body).tap do |json|
  end
end

def find_direction(json, bad_locations)
  ["north", "east", "south", "west"].each do |dir|
    if json["goal"].include?(dir) && json.has_key?(dir) && !bad_locations.include?(json[dir])
      return json[dir]
    end
  end

  nil
end

def pick_from_other_directions(json, bad_locations)
  ["north", "east", "south", "west"].each do |dir|
    if json.has_key?(dir) && !bad_locations.include?(json[dir])
      return json[dir]
    end
  end
  nil
end

def drive_page(starting_point)
  bad_locations = {}
  previous_location = []
  current_location = starting_point
  iteration = 1
  loop do
    puts "Iteration #{iteration}"
    bad_locations[current_location] ||= []
    begin
      json = get_page(current_location)
    rescue
      binding.pry
    end
    if !json.has_key?("goal") || !(json["goal"].include?("lion") || json["goal"].include?("north") || json["goal"].include?("east"))
      puts json
      break
    end
    new_location = find_direction(json, bad_locations[current_location])

    if new_location.nil?
      new_location = pick_from_other_directions(json, bad_locations[current_location])
      if new_location.nil? || new_location == starting_point
        bad_locations[previous_location.last].push(current_location)
        current_location = previous_location.pop
      elsif previous_location.include?(new_location)
        puts "Cyclical?" if previous_location.last != new_location
        bad_locations[current_location].push(new_location)
      else
        previous_location.push(current_location)
        current_location = new_location
      end
    else
      previous_location.push(current_location)
      current_location = new_location
    end
    iteration += 1
  end
end

drive_page('http://jobs.happier.com/1111')
