import axios from 'axios';
import { coingeckooBasePath } from './constants.js';

export const getEthPrice = async() => {
	return (await axios.get(`${coingeckooBasePath}/simple/price?ids=ethereum&vs_currencies=usd`)).data?.ethereum?.usd
}

export const getBtcPrice = async() => {
	return (await axios.get(`${coingeckooBasePath}/simple/price?ids=bitcoin&vs_currencies=usd`)).data?.bitcoin?.usd
}


export  const formatHiveosResponse = (res) => {
	if (!res) return 'response format error';
	const formatedResponse = {
		realtimeHashRate: (res.hashrate / 1024) / 1024,
		hashRate24h: (res.hashrate24h / 1024) / 1024,
		reportedHashrate: (res.reportedHashrate / 1024) / 1024,
		reportedHashrate24h: (res.reportedHashrate24h / 1024) / 1024,
		online: false,
		validRate: res.sharesStatusStats?.validCount,
		staleRate: res.sharesStatusStats?.staleCount
	}
	return formatedResponse
}

export const logMe = (command, user) => console.log(command, user);
export const logError = (err, reply) => {
	console.log(err.message);
	reply.text("Something went wrong :(");
}