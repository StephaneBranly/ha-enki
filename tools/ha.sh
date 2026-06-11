docker run --network host --name ha --rm  -v ./custom_components/:/config/custom_components/ -v ha-enki-test:/config -p 8123:8123 homeassistant/home-assistant
