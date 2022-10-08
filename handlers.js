import { getBtcPrice, getEthPrice } from './helpers.js';

export const priceHandler = async(query, bot, coin) => {
	try {
		const reply = bot.reply(query.message.chat);
		switch (coin) {
			case "eth":
				reply.text(`ETH: ${await getEthPrice()}`);
				break;
			case "btc":
				reply.text(`BTC: ${await getBtcPrice()}`);
				break;
			default:
				reply.text("?");
				break;
		}
		reply.deleteMessage(query.message);
	} catch (err) {
		console.log(err);
	}
}