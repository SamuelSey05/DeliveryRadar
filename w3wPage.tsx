import what3words, {
  ApiVersion,
  Transport,
  What3wordsService,
  axiosTransport,
} from "@what3words/api";

const apiKey = "Z1VKLOER";
const config: {
  host: string;
  apiVersion: ApiVersion;
} = {
  host: "https://api.what3words.com",
  apiVersion: ApiVersion.Version3,
};
const transport: Transport = axiosTransport();
const w3wService: What3wordsService = what3words(apiKey, config, { transport });
