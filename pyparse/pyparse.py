
import ctypes
import json
import os.path
import pathlib

class ParseSession:
	""" ParseSession Python wrapper of C++ ParseSession
	"""

	parselib_path = str(pathlib.Path(__file__).parent.parent / "build/libparselib.so")
	parselib = ctypes.cdll.LoadLibrary(parselib_path)
	parselib.get_json.restype = ctypes.c_char_p

	def __init__(self, log_level: int = 1):
		self.sess = ParseSession.parselib.new_session(log_level)
		self.grammar_loaded = False
		self.unprocessed_file = ""

	def load_grammar(self, filepath: str, verbose: bool = False) -> None:
		""" Loads grammar from file

		:param filepath: str file path
		:param verbose: set to True for verbose output
		"""
		self.grammar_loaded = False
		if os.path.isfile(filepath) and self.sess:
			ParseSession.parselib.load_grammar(self.sess, filepath.encode(), verbose)
			self.grammar_loaded = True
		else:
			print("err > grammar not loaded ", filepath)

	def parse_to_json_file(self, filepath: str, verbose: bool = False) -> None:
		""" Parse source file into json file. Must be called after loading grammar

		:param filepath: str file path to source code
		:param verbose: set to True for verbose
		"""
		if os.path.isfile(filepath) and self.sess and self.grammar_loaded:
			ParseSession.parselib.store_json(self.sess, filepath.encode(), verbose)
		else:
			self.unprocessed_file = filepath

	def parse_to_json(self, filepath: str, verbose: bool = False) -> dict:
		""" Parse source file into json data structure. Must be called after loading grammar

		:param filepath: str file path to source code
		:param verbose: set to True for verbose
		"""
		output = None
		if os.path.isfile(filepath) and self.sess and self.grammar_loaded:
			jsonstr = ParseSession.parselib.get_json(self.sess, filepath.encode(), verbose)
			output = json.loads(jsonstr.decode())
		else:
			self.unprocessed_file = filepath
		return output

	def __del__(self) -> None:
		""" Calls destroyer from C/ctype interface
		"""
		ParseSession.parselib.del_session(self.sess)
		self.sess = None


if __name__ == "__main__":
	psess = ParseSession()
	psess.load_grammar("../data/grammar.grm")
	del psess
