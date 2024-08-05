.PHONY: test prod kill

IP = 127.0.0.1
PORT = 443
TEST_IP = 127.0.0.1
TEST_PORT = 4443

test:
	sudo python3 py3Backend.py $(TEST_IP) $(TEST_PORT)
prod:
	nohup sudo python3 py3Backend.py $(IP) $(PORT) &
kill:
	sudo pkill python3
