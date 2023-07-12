#!/bin/bash
for i in $(seq 1 1 32)
do
  diff -s /data/recherche/python/UDASE-CHiME2023/UDASE2023_CHiME_listening_test/UDASE2023_CHiME_listening_test/js/subject_$i.json /data/recherche/python/UDASE-CHiME2023/listening-test-config/config_files/modified_json2/subject_$i.json
done




