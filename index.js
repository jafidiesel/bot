const botgram = require("botgram")
require('dotenv').config()
const axios = require('axios').default;

const bot = botgram(process.env.TELEGRAM_KEY)

const logMe = (command, user) => console.log(command, user);

// add here a middleware to log all the messages on the console

const formatHiveosResponse = (res) => {
	if (!res) return 'response format error';
	const formatedResponse = {
		realtimeHashRate: (res.hashrate/1024)/1024,
		hashRate24h: (res.hashrate24h/1024)/1024,
		reportedHashrate: (res.reportedHashrate/1024)/1024,
		reportedHashrate24h: (res.reportedHashrate24h/1024)/1024,
		online: true,
		validRate: res.sharesStatusStats?.validCount,
		staleRate: res.sharesStatusStats?.staleCount
	}
	return formatedResponse
}

bot.command("start", "help", (msg, reply) => {
	logMe("/start", msg.from.username)
	reply.text("Chat started from " + msg.from.username)
})

bot.command("docs", (msg, reply) => {
	logMe("/docs", msg.from.username)
	reply.text("Read the docs")
	reply.text("https://github.com/botgram/botgram/blob/master/docs/message.md")
})

bot.command("pickleOnline", (msg, reply) => {
	logMe("/pickleOnline", msg.from.username)
	axios.get(`https://hiveon.net/api/v1/stats/miner/${process.env.PICKLERIG_ADDRESS}/ETH`)
		.then( res => {
			const response = formatHiveosResponse(res.data);
			reply.text(response.online ? "Yes" : "No")
		})
		.catch( err => {
			console.log(err);
			reply.text(err);
		});
})

bot.command("pickle", (msg, reply) => {
	logMe("/pickle", msg.from.username)
	axios.get(`https://hiveon.net/api/v1/stats/miner/${process.env.PICKLERIG_ADDRESS}/ETH`)
		.then( res => {
			const response = formatHiveosResponse(res.data);
			reply.markdown(`_Picklerig_
			*Realtime Hashrate*: ${response.realtimeHashRate.toFixed(2)}
			*24h Hashrate*: ${response.hashRate24h.toFixed(2)}
			*Reported Hashrate*: ${response.reportedHashrate.toFixed(2)}
			*Reported Hashrate 24h*: ${response.reportedHashrate24h.toFixed(2)}
			*Online?*: ${response.online ? "Yes": "No"}
			*Valid Rate*: ${response.validRate}
			*Stale Rate*: ${response.staleRate}`)
			reply.text(`https://hiveon.net/eth/overview?miner=0x${process.env.PICKLERIG_ADDRESS}`)
		})
		.catch( err => {
			console.log(err);
			reply.text("Something went wrong :(");
		});
})