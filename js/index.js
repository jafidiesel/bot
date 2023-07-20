import botgram from 'botgram'
import dotenv from 'dotenv'
dotenv.config()
import axios from 'axios';

import https from "https";
import { formatHiveosResponse, logError, logMe } from './helpers.js';
import { priceHandler } from './handlers.js';

const myAgent = new https.Agent({ keepAlive: true, maxFreeSockets: 5 });
const bot = botgram(process.env.TELEGRAM_KEY, { agent: myAgent })

// TODO: add here a middleware to log all the messages on the console

bot.callback(function (query, next) {
	if (query.data === "getPrice.eth") priceHandler(query, bot, "eth");
	if (query.data === "getPrice.btc") priceHandler(query, bot, "btc");
  });

bot.command("start", "help", (msg, reply) => {
	logMe("/start", msg.from.username)
	reply.text("Chat started from " + msg.from.username)
})


bot.command("pickleOnline", (msg, reply) => {
	logMe("/pickleOnline", msg.from.username)
	// refactor this
	axios.get(`https://hiveon.net/api/v1/stats/miner/${process.env.PICKLERIG_ADDRESS}/ETH`)
		.then(res => {
			const response = formatHiveosResponse(res.data);
			reply.text(response.online ? "Yes" : "Sadly, No")
		})
		.catch(err => {
			logError(err, reply);
		});
})

bot.command("pickle", (msg, reply) => {
	logMe("/pickle", msg.from.username)
	// refactor this
	axios.get(`https://hiveon.net/api/v1/stats/miner/${process.env.PICKLERIG_ADDRESS}/ETH`)
		.then(res => {
			const response = formatHiveosResponse(res.data);
			reply.markdown(`_Picklerig_
			*Realtime Hashrate*: ${response.realtimeHashRate.toFixed(2)}
			*24h Hashrate*: ${response.hashRate24h.toFixed(2)}
			*Reported Hashrate*: ${response.reportedHashrate.toFixed(2)}
			*Reported Hashrate 24h*: ${response.reportedHashrate24h.toFixed(2)}
			*Online?*: ${response.online ? "Yes" : "No"}
			*Valid Rate*: ${response.validRate}
			*Stale Rate*: ${response.staleRate}`)
			reply.text(`https://hiveon.net/eth/overview?miner=0x${process.env.PICKLERIG_ADDRESS}`)
		})
		.catch(err => {
			logError(err, reply);
		});
})

bot.command("price", (msg, reply) => {
	logMe("/price", msg.from.username)
	try {
		reply.inlineKeyboard([
		  [ 
			{ text: "Eth", callback_data: "getPrice.eth" },
			{ text: "Btc", callback_data: "getPrice.btc" }
		   ]
		]).message(msg);
	  } catch (err) {
		reply.text("Something exploded.");
	  }
})

bot.command("test", (msg, reply) => {
	logMe("/test", msg.from.username);
	reply.text("More here to come.");
})
