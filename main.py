import sys
from crawler_goolge_search import main_google_search
from crawler_podcasts import main_apple_podcast

def check_start_argvs():
	if sys.argv[1] not in ["google", "podcast"]:
		raise ValueError("Only the parameter `google` or `podcast` can launch program.")

if __name__ == "__main__":
	check_start_argvs()
	
	if sys.argv[1] == "google":
		main_google_search()
	elif sys.argv[1] == "podcast":
		main_apple_podcast()
	else:
		print("Unavailable parameter.")
	input("main.py exit.")