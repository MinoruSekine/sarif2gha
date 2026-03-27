CURL ?= curl
CURL_OPTS ?= -fsSL --retry 3 --retry-delay 2 --retry-all-errors --connect-timeout 10 --max-time 120

RAW_URL_BASE := https://github.com/microsoft/sarif-tutorials/raw
RAW_HASH_ID := 819b0f62f47ecde9a8f24dfc387c41926f5edabe
RAW_URL_SAMPLES_1 := $(RAW_URL_BASE)/$(RAW_HASH_ID)/samples/1-Introduction
RAW_URL_SAMPLES_2 := $(RAW_URL_BASE)/$(RAW_HASH_ID)/samples/2-Basics
RAW_URL_SAMPLES_3 := $(RAW_URL_BASE)/$(RAW_HASH_ID)/samples/3-Beyond-basics

SAMPLE_SARIF_FILES := simple-example.sarif empty-log.sarif.json bad-eval-related-locations.sarif bad-eval-with-code-flow.sarif

all: $(SAMPLE_SARIF_FILES)

clean:
	rm -f $(SAMPLE_SARIF_FILES)

simple-example.sarif:
	$(CURL) $(CURL_OPTS) -o $@ $(RAW_URL_SAMPLES_1)/$@

empty-log.sarif.json:
	$(CURL) $(CURL_OPTS) -o $@ $(RAW_URL_SAMPLES_2)/$@

bad-eval-related-locations.sarif:
	$(CURL) $(CURL_OPTS) -o $@ $(RAW_URL_SAMPLES_3)/$@

bad-eval-with-code-flow.sarif:
	$(CURL) $(CURL_OPTS) -o $@ $(RAW_URL_SAMPLES_3)/$@

.PHONY: all clean
