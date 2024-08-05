import urllib.request, io

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class WebScraper():
	encoding = "utf-8";
	def __init__(self):
		print("Initialized Web Scraper.");
	
	def scrape(self, url):
		contents = urllib.request.urlopen(url).read();
		contents = str(contents, self.encoding);
		return contents;

	def scrape_visitBrussels(self, printContents = True, writeToFile = False):
		url = "https://www.visit.brussels/en/visitors/agenda/event-highlights";

		print("Scraping {}; printContents = {}, writeToFile = {}".format(url, printContents, writeToFile));

		contents = self.scrape(url);
	
		# start at list of events
		start = '<div class="cmp-list-carousel u-background-color--inherited " style="background:">';
		# ending of events div
		end = '</noscript>';

		startIndex = contents.find(start);
		contents = contents[startIndex:len(contents)];
		contents = contents[contents.find('<noscript>'):];
		endIndex = contents.find(end);
		contents = contents[:endIndex];

		# skip to first title
		contents = contents[contents.find("<h3>"):];

		# split text up into separate events
		contents = contents.split("<h3>");

		if(writeToFile):
			# clear file
			file = open("scrapeOutput_visit_brussels.txt", "w");
			file.write("");
			file.close()
			# start appending data
			file = open("scrapeOutput_visit_brussels.txt", "w");
		# print all events, titles only.
		for x in contents:
			if(len(x) <= 0): 
				continue;
			title = x[:x.find("</h3>")];
			if(writeToFile):
				file.write('.' + '-' * (len(title)+1) + '.\n');
				file.write('|' + title + " |\n");
				file.write('\'' + '-' * (len(title)+1) + '\'\n');
			if(printContents):
				print(bcolors.BOLD + bcolors.UNDERLINE + bcolors.OKGREEN + title + bcolors.ENDC * 3);
			x = x[len(title) + len("</h3>"):];
			paragraphs = x.split("<p>");
			for p in paragraphs:
				p = p[:p.find("</p>")];
				p = p.strip();
				if(len(p) > 0):
					if(writeToFile):
						file.write(p + "\n");
					if(printContents):
						print(p);
					break;
			if(writeToFile):
				file.write("\n");
			if(printContents):
				print("");
		if(writeToFile):
			file.close();