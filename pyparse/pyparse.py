
import ctypes
import json
import os.path
import pathlib

def check_install(verbose: bool = True):
	pyparse_parent_folder = pathlib.Path(pathlib.Path(__file__).parent)
	parselib_parent_folder = pathlib.Path(pyparse_parent_folder / "parselibbuild/")
	parselib_path = pathlib.Path(parselib_parent_folder / "libparselib.so")
	install_script_path = pathlib.Path(__file__).parent / "parselibInstall.sh"

	if not parselib_path.is_file():
		print(f"Seems like parselib: '{str(parselib_path)}' is not installed.. installing")
		with open(install_script_path, "w") as fs:
			fs.writelines([
				"#!/bin/bash\n",
				f"cd {pyparse_parent_folder}\n",
				"git clone https://github.com/omarboukhris/parselibcpp.git\n",
				f"mkdir {parselib_parent_folder}\n",
				f"cd {parselib_parent_folder}\n",
				"cmake ../parselibcpp\n",
				"make -j8\n",
			])

		with os.popen(f"sh {install_script_path}") as pipe:
			out = pipe.readlines()
			print("\n".join(out))

		print("Installed parselib")
		return True

class ParseSession:
	""" ParseSession Python wrapper of C++ ParseSession
	"""
	_parselib_exists = check_install()
	parselib_path = str(pathlib.Path(__file__).parent / "parselibbuild/libparselib.so")
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
