-- Wireshark Protocol Dissector for the Napoleon eFIRE controller protocol
-- (c) 2023 Felix Kaechele <felix@kaechele.ca>

-- Copy this file into your Wireshark plugins directory:
-- https://www.wireshark.org/docs/wsug_html_chunked/ChPluginFolders.html

-- luacheck: globals DissectorTable Proto ProtoExpert ProtoField Struct base expert

local p_efire = Proto("efire", "Napoleon eFIRE")

local t_msg_type = { [0xaa] = "Request", [0xbb] = "Response" }

local t_commands = {
	-- R = Read Command (Command sent without parameters, response received with state/data)
	-- W = Write Command (Command sent with parameters, response received with return code)
	[0x27] = "Set Night Light/Standing Pilot", -- W
	[0x28] = "Set Split Flow/Blower Speed/Aux/Flame Height", -- W
	[0xb1] = "Set LED State", -- W
	[0xc1] = "Set LED Color", -- W
	[0xc3] = "Set Timer", -- W
	[0xc4] = "Set Power State", -- W
	[0xc5] = "Send Password", -- W (authenticate or set password if used after sending 0xc6)
	[0xc6] = "Manage Password", -- W
	[0xc7] = "Set Time Sync", -- W
	[0xe0] = "Query LED State", -- R
	[0xe1] = "Query LED Color", -- R
	[0xe2] = "Query LED Effect", -- R
	[0xe3] = "Query Pilot/Night Light/Main Mode State", -- R
	[0xe4] = "Query Split Flow/Blower Speed/Aux/Flame Height State", -- R
	[0xe6] = "Query Timer", -- R
	[0xe7] = "Query Power State", -- R
	[0xe8] = "Read Password", -- R
	[0xe9] = "Set Password", -- W (has no parameters, simply commits the previously sent password to memory)
	[0xea] = "Time Sync Response", -- -R (queries an active timer from the controller for the time that's left on it)
	[0xeb] = "LED Controller State Response", -- R (not seen in testing yet)
	[0xee] = "Aux Control State Response", --R
	[0xf1] = "Set LED Controller Effect", --W
	[0xf2] = "Query BLE Version", --R
	[0xf3] = "Query MCU Version", --R
	[0xf4] = "Query Aux Control", --R
}

local t_power_states = {
	[0x00] = "Off",
	[0xff] = "On",
}

local t_password_actions = {
	[0x3f] = "Reset Password",
	[0xf5] = "Set Password",
}

local t_c5_return_codes = {
	[0x00] = "Password set",
	[0x01] = "Password set failed",
	[0x19] = "Invalid Password",
	[0x35] = "Login Successful",
}

local t_password_set_return_codes = {
	[0x53] = "Success",
	[0x25] = "Error",
}

local t_light_states = {
	[0x0] = false,
	[0xffffff] = true,
}

local t_light_modes = {
	[0xffffff] = "Ember Bed",
	[0x020202] = "Hold",
	[0x010101] = "Cycle",
}

local t_light_modes_short = {
	[0xff] = "Ember Bed",
	[0x02] = "Hold",
	[0x01] = "Cycle",
}

-- Functions that follow the generic return code schema (see return codes below)
local t_generic_return = {
	[0x27] = true,
	[0x28] = true,
	[0xb1] = true,
	[0xc1] = true,
	[0xc3] = true,
	[0xc4] = true,
	[0xc6] = true,
	[0xc7] = true,
	[0xf1] = true,
}

local t_generic_return_codes = {
	[0x00] = "Success",
	[0x01] = "Error",
}

-- Common fields
local f_header = ProtoField.uint8("efire.header", "Header", base.HEX)
local f_msg_type = ProtoField.uint8("efire.msg_type", "Message Type", base.HEX, t_msg_type)
local f_payload_length = ProtoField.uint8("efire.payload_length", "Length")
local f_parameters = ProtoField.bytes("efire.parameters", "Parameters")
local f_checksum = ProtoField.uint8("efire.checksum", "Checksum", base.HEX)
local f_footer = ProtoField.uint8("efire.footer", "Footer", base.HEX)

-- Request fields
local f_command = ProtoField.uint8("efire.command", "Command", base.HEX, t_commands)

local f_login_password = ProtoField.string("efire.login_password", "Password")
local f_password_action = ProtoField.uint8("efire.password_action", "Action", base.HEX, t_password_actions)
local f_power_request = ProtoField.uint8("efire.power_request", "Requested state", base.HEX, t_power_states)

-- Response fields
local f_response_class = ProtoField.uint8("efire.response_class", "Response Class", base.HEX, t_commands)

local f_aux = ProtoField.bool("efire.aux", "Aux Relay on")
local f_aux_control = ProtoField.bool("efire.aux_control", "Aux Control detected")
local f_ble_version = ProtoField.string("efire.ble_version", "BLE Version")
local f_blower_speed = ProtoField.uint8("efire.blower_speed", "Blower Speed")
local f_flame_height = ProtoField.uint8("efire.flame_height", "Flame Height")
local f_light_color = ProtoField.string("efire.light_color", "Light color")
local f_light_mode = ProtoField.uint24("efire.light_mode", "Light mode", base.HEX, t_light_modes)
local f_light_mode_short = ProtoField.uint8("efire.light_mode_short", "Light mode", base.HEX, t_light_modes_short)
local f_light_state = ProtoField.bool("efire.light_state", "Light on")
local f_login_result = ProtoField.uint8("efire.login_result", "Login result", base.HEX, t_c5_return_codes)
local f_main_mode = ProtoField.uint8("efire.main_mode", "Main Mode")
local f_mcu_version = ProtoField.string("efire.mcu_version", "MCU Version")
local f_night_light = ProtoField.uint8("efire.night_light", "Night Light Level")
local f_pilot_state = ProtoField.bool("efire.pilot_state", "Pilot State on")
local f_power_state = ProtoField.bool("efire.power_state", "Fireplace on")
local f_set_password_result =
	ProtoField.uint8("efire.set_password_result", "Result", base.HEX, t_password_set_return_codes)
local f_split_flow = ProtoField.bool("efire.split_flow", "Split Flow Valve on")
local f_timer_enabled = ProtoField.bool("efire.timer_hours", "Enabled")
local f_timer_hours = ProtoField.uint8("efire.timer_hours", "Hours")
local f_timer_minutes = ProtoField.uint8("efire.timer_hours", "Minutes")
local f_timer_seconds = ProtoField.uint8("efire.timer_hours", "Seconds")

-- Generic fields
local f_set_command_result = ProtoField.uint8("efire.cmd_result", "Command Result", base.HEX, t_generic_return_codes)

p_efire.fields = {
	f_aux_control,
	f_aux,
	f_ble_version,
	f_blower_speed,
	f_checksum,
	f_command,
	f_flame_height,
	f_footer,
	f_header,
	f_light_color,
	f_light_mode,
	f_light_state,
	f_login_password,
	f_login_result,
	f_main_mode,
	f_mcu_version,
	f_msg_type,
	f_night_light,
	f_parameters,
	f_password_action,
	f_payload_length,
	f_pilot_state,
	f_power_request,
	f_power_state,
	f_response_class,
	f_set_command_result,
	f_set_password_result,
	f_split_flow,
	f_timer_enabled,
	f_timer_hours,
	f_timer_minutes,
	f_timer_seconds,
}

local x_checksum = ProtoExpert.new("efire.calculated_checksum", "Checksum", expert.group.CHECKSUM, expert.severity.CHAT)

p_efire.experts = { x_checksum }

-- calculate the checksum for eFIRE payloads
-- it's essentially an XOR over all fields except for header (byte 0), msg_type (byte 1) and footer (last byte)
local function calc_checksum(msg)
	local bytes, _ = msg(2, msg:len() - 4):bytes()
	local csum = 0x00
	for i = 0, bytes:len() - 1 do
		csum = bit.bxor(csum, bytes:get_index(i))
	end
	return csum
end

local function checksum_is_valid(msg)
	if calc_checksum(msg) == msg(msg:len() - 2, 1):uint() then
		return expert.severity.CHAT, "Checksum valid"
	end
	return expert.severity.WARN, "Checksum invalid"
end

function p_efire.dissector(buffer, pinfo, root)
	pinfo.cols.protocol:set("eFIRE")

	local pktlen = buffer:reported_length_remaining()
	-- Packet format: header, msg_type, payload, footer
	-- Payload format: payload_length, command, parameters, checksum
	local payload_len = buffer(2, 1):uint()
	local msg_type = buffer(1, 1):uint()
	local command = buffer(3, 1):uint()
	local parameters, _ = buffer(4, payload_len - 3):bytes()

	if pktlen < 6 then
		print("packet length", pktlen, "too short")
		return
	end

	local subtree = root:add(p_efire, buffer(0, pktlen), "Napoleon eFIRE Protocol Data")
	subtree:add(f_header, buffer(0, 1))
	subtree:add(f_msg_type, buffer(1, 1))
	subtree:add(f_payload_length, buffer(2, 1))

	if msg_type == 0xaa then
		if t_commands[command] then
			pinfo.cols.info = "eFIRE Controller Command (" .. t_commands[command] .. ")"
		else
			pinfo.cols.info = "eFIRE Controller Command (Unknown Class " .. string.format("0x%x", command) .. ")"
		end
		subtree:add(f_command, buffer(3, 1))
	elseif msg_type == 0xbb then
		if t_commands[command] then
			pinfo.cols.info = "eFIRE Controller Response (" .. t_commands[command] .. ")"
		else
			pinfo.cols.info = "eFIRE Controller Response (Unknown Class " .. string.format("0x%x", command) .. ")"
		end
		subtree:add(f_response_class, buffer(3, 1))
	end

	local param_tree = subtree:add(f_parameters, buffer(4, payload_len - 3))

	-- Let's look at requests
	if msg_type == 0xaa then
		-- Set Night Light/Standing Pilot/Main Mode
		-- These are commands that affect the fireplace regardless of flame state
		if command == 0x27 then
			local night_light_level = bit.band(bit.rshift(parameters:get_index(1), 4), 7)
			local standing_pilot = bit.rshift(parameters:get_index(1), 7)
			param_tree:add(f_night_light, buffer(5, 1), night_light_level):set_generated()
			param_tree:add(f_pilot_state, buffer(5, 1), standing_pilot):set_generated()
		end

		-- Set Split Flow/Blower/Aux/Flame Height
		-- These commands affect the fireplace during heating operation
		if command == 0x28 then
			local param = parameters:get_index(1)
			local split_flow = bit.band(bit.rshift(param, 7), 1)
			local blower_speed = bit.band(bit.rshift(param, 4), 7)
			local aux = bit.band(bit.rshift(param, 3), 1)
			local flame_height = bit.band(param, 7)
			param_tree:add(f_split_flow, buffer(4, 1), split_flow):set_generated()
			param_tree:add(f_blower_speed, buffer(4, 1), blower_speed):set_generated()
			param_tree:add(f_aux, buffer(4, 1), aux):set_generated()
			param_tree:add(f_flame_height, buffer(4, 1), flame_height):set_generated()
		end

		-- Set Light state
		if command == 0xb1 then
			local state = Struct.unpack(">I3", parameters:raw())
			print(state)
			param_tree
				:add(f_light_state, buffer(4, 3), (t_light_states[state] and t_light_states[state]))
				:set_generated()
		end

		-- Set Color
		if command == 0xc1 then
			param_tree
				:add(
					f_light_color,
					buffer(4, 3),
					"R: "
						.. parameters:get_index(0)
						.. " G: "
						.. parameters:get_index(1)
						.. " B: "
						.. parameters:get_index(2)
				)
				:set_generated()
		end

		-- Timer
		if command == 0xc3 then
			param_tree:add(f_timer_hours, buffer(4, 1), parameters:get_index(0))
			param_tree:add(f_timer_minutes, buffer(5, 1), parameters:get_index(1))
			param_tree:add(f_timer_enabled, buffer(6, 1), parameters:get_index(2))
		end

		-- Power
		if command == 0xc4 then
			param_tree:add(f_power_request, buffer(4, 1), parameters:get_index(0))
		end

		-- Login & Change Password
		if command == 0xc5 then
			param_tree:add(f_login_password, buffer(4, payload_len - 3), buffer(4, payload_len - 3):string())
		end

		-- Password Management
		if command == 0xc6 then
			param_tree:add(f_password_action, buffer(4, 1), parameters:get_index(0))
		end
	elseif msg_type == 0xbb then
		-- Generic set command results
		if t_generic_return[command] then
			param_tree:add(f_set_command_result, buffer(4, 1), parameters:get_index(0))
		end

		-- Login result
		if command == 0xc5 then
			param_tree:add(f_login_result, buffer(4, 1), parameters:get_index(0))
		end

		-- Light State
		if command == 0xe0 then
			param_tree:add(
				f_light_state,
				buffer(4, 3),
				parameters:get_index(0) == parameters:get_index(1) == parameters:get_index(2) == 0xff
			)
		end

		-- Light Color
		if command == 0xe1 then
			param_tree:add(
				f_light_color,
				buffer(4, 3),
				"R: "
					.. parameters:get_index(0)
					.. " G: "
					.. parameters:get_index(1)
					.. " B: "
					.. parameters:get_index(2)
			)
		end

		-- Light mode
		if command == 0xe2 then
			local lm = Struct.unpack(">I3", parameters:raw())
			param_tree:add(f_light_mode, buffer(4, 3), lm)
		end

		-- Response 0xe3
		-- Continuous Pilot / Night Light / Main Mode
		-- Continuous Pilot: Indicates whether the continuous pilot is on or off
		-- Night Light: Indicates the Night Light brightness (0/off to 6/max)
		-- Main Mode: Indicates Operation Mode (0: off / 1: manual / 2: thermostat / 3: smart)
		if command == 0xe3 then
			local pilot_state = bit.band(bit.rshift(parameters:get_index(0), 7), 1)
			local night_light = bit.band(bit.rshift(parameters:get_index(0), 4), 7)
			local main_mode = bit.band(parameters:get_index(0), 7)

			param_tree:add(f_pilot_state, buffer(5, 1), pilot_state)
			param_tree:add(f_night_light, buffer(5, 1), night_light)
			param_tree:add(f_main_mode, buffer(5, 1), main_mode)
		end

		-- Response 0xe4
		-- Split Flow/Blower Speed/Aux/Flame Height State
		-- Split Flow: Indicates whether the Split Flow Valve is on or off
		-- Blower Speed: Indicates the blower speed (0/off to 6/max)
		-- Aux: Indicates the state of the 120V AUX relay (connector X13 on the ProFlame controller)
		-- Flame Height: Indicates the Flame Height setting (0/off to 6/max)
		if command == 0xe4 then
			local split_flow = bit.band(bit.rshift(parameters:get_index(0), 7), 1)
			local blower_speed = bit.band(bit.rshift(parameters:get_index(0), 4), 7)
			local aux = bit.band(bit.rshift(parameters:get_index(0), 3), 1)
			local flame_height = bit.band(parameters:get_index(0), 7)

			param_tree:add(f_split_flow, buffer(5, 1), split_flow)
			param_tree:add(f_blower_speed, buffer(5, 1), blower_speed)
			param_tree:add(f_aux, buffer(5, 1), aux)
			param_tree:add(f_flame_height, buffer(5, 1), flame_height)
		end

		-- Timer State
		if command == 0xe6 then
			param_tree:add(f_timer_hours, buffer(4, 1), parameters:get_index(0))
			param_tree:add(f_timer_minutes, buffer(5, 1), parameters:get_index(1))
			if parameters:len() > 3 then
				param_tree:add(f_timer_seconds, buffer(7, 1), parameters:get_index(3))
			end
			param_tree:add(f_timer_enabled, buffer(6, 1), parameters:get_index(2))
		end

		-- Power State
		if command == 0xe7 then
			param_tree:add(f_power_state, buffer(4, 1), parameters:get_index(0) == 0xff)
		end

		-- Password Read
		if command == 0xe8 then
			param_tree:add(f_login_password, buffer(4, payload_len - 3), buffer(4, payload_len - 3):string())
		end

		-- Password Set
		if command == 0xe9 then
			param_tree:add(f_set_password_result, buffer(4, 1), parameters:get_index(0))
		end

		-- Time Sync
		if command == 0xea then
			param_tree:add(f_timer_hours, buffer(4, 1), parameters:get_index(0))
			param_tree:add(f_timer_minutes, buffer(5, 1), parameters:get_index(1))
			param_tree:add(f_timer_seconds, buffer(6, 1), parameters:get_index(2))
		end

		-- Light Mode
		if command == 0xeb then
			local light_state = parameters:get_index(0) == 0xff
			local light_r = bit.band(parameters:get_index(1), 0xff)
			local light_g = bit.band(parameters:get_index(2), 0xff)
			local light_b = bit.band(parameters:get_index(3), 0xff)
			param_tree:add(f_light_state, buffer(4, 1), light_state)
			param_tree:add(f_light_color, buffer(5, 3), "R: " .. light_r .. " G: " .. light_g .. " B: " .. light_b)
			param_tree:add(f_light_mode_short, buffer(8, 1), parameters:get_index(4))
		end

		-- Aux Control
		if command == 0xee then
			param_tree:add(f_aux_control, buffer(4, 1), parameters:get_index(0) == 0x00)
		end

		-- BLE Version
		if command == 0xf2 then
			param_tree:add(f_ble_version, buffer(5, 1), parameters:get_index(1))
		end

		-- MCU Version
		if command == 0xf3 then
			local mcu_version = parameters:get_index(0) .. "." .. parameters:get_index(1) .. parameters:get_index(2)
			param_tree:add(f_mcu_version, mcu_version)
		end
	end

	subtree:add(f_checksum, buffer(payload_len + 1, 1))
	local _, csum_message = checksum_is_valid(buffer)
	subtree:add_proto_expert_info(x_checksum, csum_message)
	subtree:add(f_footer, buffer(payload_len + 2, 1))
end

DissectorTable.get("btatt.handle"):add(0x0020, p_efire)
DissectorTable.get("btatt.handle"):add(0x001e, p_efire)
