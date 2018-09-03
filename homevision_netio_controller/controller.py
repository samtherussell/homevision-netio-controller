
import socket

class UserException(Exception):
  pass

def user_exception(s): raise UserException(s)

class Macro:
  """Represents a macro to be run"""
  def __init__(self, code):
    """code: int - index of macro to run"""
    self.code = code

class Command:
  """Represents a macro to be run"""
  def __init__(self, command):
    """command: string - command to send"""
    self.command = command
    
class HomeVisionController:

  def __init__(
    self,
    ip_address,
    port,
    auth,
    on_off_appliance_codes={},
    actions={},
    process_actions={},
    var_queries={},
    flag_queries={},
    flag_return_values = {True: ["True", "On", "Yes", "Occupied", "Set", "1"], False: ["False", "Off", "No", "Vacant", "Clear", "0"]},
    on_off_commands = None
  ):
    """
    Args:
      ip_address: string
      port: int
      auth: string
        - key for authenticating with netio
      on_off_appliance_codes: dict[string] => int - codes to be fed to 'on_off_commands' for each appliance
      actions: dict[string] => Macro/Command/(_, _, ...) - named actions to be completed
      process_actions: dict[string] => {"START": X, "STOP": X} where X is Macro/Command/(_, _, ...) - named processes to be started and stopped
      var_queries: dict[string] => int - mapping of names to variable indexes
      flag_queries: dict[string] => int - mapping of names to flag indexes
      flag_return_values: {True: [string], False: [string]} - synonyms for true and false that are returned by netio 'read flag command'. (ignore if you haven't set them up)
      on_off_commands: {"ON": (int) => Macro/Command/(_, _, ...), "OFF": (int) => Macro/Command} - how to handle on and off commands
    """
    self.ip_address = ip_address
    self.port = port
    self.auth = auth
    self.on_off_appliance_codes = on_off_appliance_codes
    self.actions = actions
    self.process_actions = process_actions
    self.var_queries = var_queries
    self.flag_queries = flag_queries
    self.flag_return_values = flag_return_values
    self.on_off_commands = on_off_commands
  
  def on_off_command(self, details):
    """Send an on or off command to an appliance
    
    Sends the specified command to the homevision through netio interface to control the specified appliance.
    
    Args:
      details: {"appliance": string, "state": string} 
    """
    if "appliance" not in details:
      raise Exception("appliance not specified")
    elif "state" not in details:
      raise Exception("state not specified")

    if details["appliance"] not in self.on_off_appliance_codes.keys():
      raise Exception("appliance not supported. Must be one of: " + ",".join(self.on_off_appliance_codes.keys()))

    appliance_code = self.on_off_appliance_codes[details["appliance"]]
    
    if details['state'] == "ON":
      self._switch_on(appliance_code)
    elif details["state"] == "OFF":
      self._switch_off(appliance_code)
    else:
      raise Exception("state not supported. Must be either \"ON\" or \"OFF\".")

  def action_command(self, details):
    """Send an action command
    
    Sends the specified command to the homevision through netio interface.
    
    Args:
      details: {"command": string} 
    """
    if "command" not in details:
      raise Exception("Command not specified")

    if details["command"] not in self.actions.keys():
      raise Exception("Command not supported. Must be one of: " + ",".join(self.actions.keys()))

    self._handle_action(self.actions[details["command"]])

  def start_stop_command(self, details):
    """Starts or stops a process
    
    Sends the specified command to the homevision through netio interface to control the specified process.
    
    Args:
      details: {"action": string, "process": string} 
    """
    if "action" not in details:
      raise Exception("action not specified")
    elif "process" not in details:
      raise Exception("process not specified")

    if details["process"] not in self.process_actions.keys():
      raise Exception("process not supported. Must be one of: " + ",".join(self.process_actions.keys()))
    
    if details['action'] == "START":
      self._handle_action(self.process_actions[details["process"]]["START"])
    elif details["action"] == "STOP":
      self._handle_action(self.process_actions[details["process"]]["STOP"])
    else:
      raise Exception("action not supported. Must be either \"START\" or \"STOP\".")
      
  def _handle_action(self, action):
    def handle_single(a):
      if type(a) == Macro:
        self._run_macro(a.code)
      elif type(a) == Command:
        self._send_command(a.command)
      elif type(a) == Exception:
        raise a
      else:
        raise Exception("Internal Error: invalid action type. Should be Macro, Command or Exception")
        
    if type(action) == tuple:
      for a in action:
        handle_single(a)
    else:
      handle_single(action)

  def var_query(self, details):
    """Returns the answer to a query on variable
    
    Returns the answer to a query on the specified variable using netio
    
    Args:
      details: {"query": string} 
    """
    if "query" not in details:
      raise Exception("query not specified")
    
    if details["query"] not in self.var_queries.keys():
      raise Exception("query not supported. Must be one of: " + ",".join(self.var_queries.keys()))
    
    code = self.var_queries[details["query"]]
    if type(code) == int:
      val = self._get_var(code)
    elif type(code) == tuple:
      val = [self._get_var(c) for c in code]
    else:
      raise Exception("Internal Exception: variable code is not valid")
      
    return val
    
  def flag_query(self, details):
    """Returns the answer to a query on flag
    
    Returns the answer to a query on the specified variable using netio
    
    Args:
      details: {"query": string} 
    """
    if "query" not in details:
      raise Exception("query not specified")
    
    if details["query"] not in self.flag_queries.keys():
      raise Exception("query not supported. Must be one of: " + ",".join(self.flag_queries.keys()))
    
    val = self._get_flag(self.flag_queries[details["query"]])
    
    return "yes" if val else "no"
    
  def _switch_on(self, code):
    if self.on_off_commands == None:
      raise Exception("No On/Off command set")
    self._handle_action(self.on_off_commands["ON"](code))
   
  def _switch_off(self, code):
    if self.on_off_commands == None:
      raise Exception("No On/Off command set")
    self._handle_action(self.on_off_commands["OFF"](code))

  def _run_macro(self, code):
    self._send_command(b'action macro run ' + bytes(str(code), encoding="ascii") + b'; __wait 100')

  def _send_command(self, command):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((self.ip_address, self.port))
    s.send(bytes("auth " + self.auth + "\n", encoding="ascii"))
    s.send(command)
    s.close()

  def _get_var(self, id):
    return int(self._run_read_command(b"get var state " + bytes(str(id), encoding="ascii")))

  def _get_flag(self, id):
    ret = self._run_read_command(b"get flag state " + bytes(str(id), encoding="ascii"))
    if ret in self.flag_return_values[False]:
      return False
    elif ret in self.flag_return_values[True]:
      return True
    else:
      raise Exception("Flag value not supported: " + ret)

  def _run_read_command(self, command):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((self.ip_address, self.port))
    s.send(bytes("auth " + self.auth + "\n", encoding="ascii"))
    s.recv(10)
    s.send(command)
    s.send(b'\n')
    response = s.recv(10).decode(encoding="ascii").rstrip()
    s.close()
    return response
    