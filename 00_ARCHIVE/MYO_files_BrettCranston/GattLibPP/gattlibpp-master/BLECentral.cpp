/*
 * BLECentral.cpp
 *
 *  Created on: Dec 16, 2017
 *        Copyright (C) 2017 Pat Deegan, https://psychogenic.com
 *  This file is part of GattLib++.
 *
 *  GattLib++ is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *  GattLib++ is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with GattLib++.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "../include/gattlibpp/BLECentral.h"

#include "../include/gattlibpp/BLECentralDebug.h"
#include "../include/gattlibpp/GattlibppPlatform.h"

#include <algorithm>
#include <string>

#define BLECENTRAL_FAKE_READASYNC



#define BLECENTRAL_TRIGGER_CB_IFSET(thecb, reason) \
	BLECNTL_DEBUGLN("Trigger fail cb: " << reason); \
	if (thecb) { \
		thecb(); \
	}

#define BLECENTRAL_ENSURE_ADAPTER_AVAIL(failcb) \
		if (! openAdapterIfRequired()) { \
				BLECENTRAL_TRIGGER_CB_IFSET(failcb, "can't open adapter?"); \
				return false; \
			}

static void clib_connected_callback(gatt_connection_t* connection) {

	Gattlib::BLECentral::getInstance()->deviceConnected(connection);
}


static void clib_disconnected_callback() {

	Gattlib::BLECentral::getInstance()->deviceDisconnected();
}



static void clib_device_discovered_callback(const char* addr, const char* name) {
	std::string addressStr, nameStr;
	if (addr) {
		addressStr = addr;
	}
	if (name) {
		nameStr = name;
	}
	Gattlib::Discovery::Device ho(addressStr, nameStr);
	Gattlib::BLECentral::getInstance()->deviceDiscovered(ho);

}
static void clib_scan_complete_callback() {
	Gattlib::BLECentral::getInstance()->scanCompleted();
}

static void *clib_read_char_callback(const void* buffer, size_t buffer_len) {
	if ((buffer && buffer_len) )
	{

		Gattlib::BLECentral::getInstance()->readDataReceived((const uint8_t*)buffer,
				buffer_len);

	}
	return NULL;

}

static void clib_generic_async_op_done() {

	Gattlib::BLECentral::getInstance()->currentOpCompleted();
}


static void clib_scan_disable_done() {

	Gattlib::BLECentral::getInstance()->scanDisableCompleted();
}



static void clib_generic_async_op_failed() {
	Gattlib::BLECentral::getInstance()->currentOpFailed();

}
static void clib_notification_handler_callback(const uuid_t* uuid,
			const uint8_t* data,
			size_t data_length, void* user_data) {
	char uuidStr[BLECENTRAL_UUIDSTRING_MAX_LENGTH + 1] = {0,};


	if (! (data && data_length)) {

		BLECNTL_ERRORLN("notif handler callback: no data/length");
		return;
	}

	if (gattlib_uuid_to_string(uuid, uuidStr, BLECENTRAL_UUIDSTRING_MAX_LENGTH) != 0) {
		BLECNTL_ERRORLN("notif handler callback: can't convert uuid??");
		return;
	}

	Gattlib::Characteristic::UUID charUUID(uuidStr);
	Gattlib::BLECentral::getInstance()->handleNotification(charUUID, data, data_length);

}


namespace Gattlib {

BLECentral * BLECentral::ble_central_singleton = NULL;


// helper
typedef std::function<bool(const Characteristic::Details &)> CharOpSupportedFunc;

static Characteristic::UUID normalizeDeviceUUID(const UUID& dev_uuid) {
	UUID duid = dev_uuid;
	return duid;
/*
 not useful
	std::transform(duid.begin(), duid.end(), duid.begin(), ::tolower);
	BLECNTL_DEBUGLN("NORMALIZED " << dev_uuid << " TO " << duid);

	return duid;
*/
}
static bool getUUIDForCharOrFail(Device::Details * dets,
		const Characteristic::UUID& charuid, CharOpSupportedFunc opSupp,
		uuid_t * into, Callbacks::Error failure)
{

	// Characteristic::UUID charuid = normalizeCharacteristic(characteristic_uuid);
	if (dets->discovery_done) {

		DEVDETS_LOCKGUARD_BEGINBLOCK(dets, "getUUID");
		if (!dets->hasCharacteristic(charuid)) {

			BLECENTRAL_TRIGGER_CB_IFSET(failure,
					"don't seem to have this char: " << charuid);
			return false;
		}
		const Characteristic::Details & charDets = dets->characteristic(charuid);
		if (! opSupp(charDets)) {

			BLECENTRAL_TRIGGER_CB_IFSET(failure, "char doesn't support operation");
			return false;
		}
		*into = charDets.gl_uuid;


		DEVDETS_LOCKGUARD_ENDBLOCK();
	} else {
		// going blind...
		if (gattlib_string_to_uuid(charuid.c_str(),
				charuid.size(), into) != 0) {
			BLECENTRAL_TRIGGER_CB_IFSET(failure,
					"conversion of uuid string to uuid_t failed");
			return false;
		}
	}

	return true;

}






void BLECentral::processAsync() {

	gattlib_async_process_all();
	if (reportQueue.size()) {
		Callbacks::Queue q = reportQueue; // local copy... callbacks might affect
		reportQueue.clear();
		for (Callbacks::Queue::iterator iter = q.begin(); iter != q.end();
				iter++) {
			(*iter)();
		}
	}

	if (asyncActions.size()) {
		AsyncAction::Details & actDets = asyncActions.front();
		if (actDets.isPending()) {
			BLECNTL_DEBUGLN("starting async action: " << actDets.name);
			actDets.run();
		} else if (actDets.isDone()) {
			BLECNTL_DEBUGLN("async action '" << actDets.name << "' is done");
			asyncActions.pop();
		} else {
			actDets.incrementWaitCount();

		}
	}
}

Device::Details * BLECentral::deviceDetails(const UUID & devId) {
	DeviceMap::iterator iter = devices.find(normalizeDeviceUUID(devId));
	if (iter == devices.end())
	{
		return NULL;
	}

	return &((*iter).second);


}

bool BLECentral::openAdapterIfRequired() {
	if (adapter_is_open) {
		return true;
	}

	return adapterOpen();
}
bool BLECentral::adapterOpen(const AdapterName & name) {
	if (adapter_is_open) {
		if (name == adapter_name) {
			return true;
		}
		adapterClose();
	}


	const char* req_name = name.size()? name.c_str() : NULL;
	if (gattlib_adapter_open(req_name, &adapter)) {
		// problem opening adapter...
		return false;
	}
	adapter_name = name;
	adapter_is_open = true;
	return true;


}
bool BLECentral::adapterClose() {
	if (! adapter_is_open) {
		return false;
	}
	gattlib_adapter_close(adapter);
	adapter_is_open = false;
	return true;
}

void BLECentral::stopAllNotifications(const UUID & device) {

	Device::Details * dev = deviceDetails(device);
	if (!dev) {
		return;
	}
	dev->foreachCharacteristic([this, dev](Characteristic::Details & aChar) {
		if (aChar.registeredForNotifs) {
			this->stopNotification(dev->id, Service::AnyService, aChar.id);
		}
	});

}

void BLECentral::shutdown() {

	bool willHandleAdapter = false;
	if (connected_to.size()) {
		Device::Details * dev = deviceDetails(connected_to);

		if (dev) {
			bool adaptCloseCalled = false;
			willHandleAdapter = true;


			stopAllNotifications(connected_to);

			auto doneCb = [this, &adaptCloseCalled](){
				adapterClose();
				adaptCloseCalled = true;
			};
			disconnect(dev->id, doneCb, doneCb);
			int waitLoopCount = 0;

			while ( (! adaptCloseCalled) && waitLoopCount++ < 1000) {
				processAsync();
				BLECNTL_SLEEP_US(2000);
			}

		}
	}

	if (! willHandleAdapter) {
		adapterClose();
	}

}


bool BLECentral::scan(SecondsValue runSeconds,
		Callbacks::SuccessNotification scanCompleted,
		Callbacks::Discovered deviceDiscoveredCb, Callbacks::Error failure) {

	BLECENTRAL_ENSURE_ADAPTER_AVAIL(failure);

	if (is_scanning) {
		/*
		AsyncAction::Details asyncAlreadyRunningAct("scanrunning", scanCompleted, failure);
		asyncAlreadyRunningAct.trigger = [](AsyncAction::Details * thisAction) {
			thisAction->completedWithSuccess();
		};

		queueAsyncAction(asyncAlreadyRunningAct);
		*/
		return true;
	}

	if (connected_to.size() && ! numAsyncActionsQueued()) {
		BLECNTL_DEBUGLN("asked to scan but we're connected and there's nothing queued to disconn... do that first");

		Device::Details * dets = deviceDetails(connected_to);
		if (dets && dets->connection) {
			// we really seem to be still connected to this thing
			AsyncAction::Details autoDisconnAction("autodisconn", [](){
				BLECNTL_DEBUGLN("auto disconn completed");
			}, [](){
				BLECNTL_DEBUGLN("hm, auto disconn failed?");
			});

			UUID devId = dets->id;

			autoDisconnAction.trigger = [this, devId](AsyncAction::Details * thisAction){

				this->disconnect(devId, [](){
				}, [](){
				});
			};

		}
	}



	devDiscoveredCb = deviceDiscoveredCb;

	AsyncAction::Details asyncAct("scan", scanCompleted, failure);
	asyncAct.trigger = [runSeconds, this](AsyncAction::Details * thisAction) {

		if (gattlib_adapter_scan_enable_async(adapter, clib_device_discovered_callback,
				runSeconds, clib_scan_complete_callback) != 0)
		{
			this->is_scanning = false;
			thisAction->completedWithFailure();
		}

	};


	queueAsyncAction(asyncAct);

	is_scanning = true;
	return true;
}
bool BLECentral::scan(const Service::UUIDList & services, SecondsValue runSeconds,
		Callbacks::SuccessNotification scanCompleted,
		Callbacks::Discovered deviceDiscoveredCb, Callbacks::Error failure) {

	// TODO:FIXME -- implement service filter?
	return scan(runSeconds, scanCompleted, deviceDiscoveredCb, failure);

}
bool BLECentral::startScan(Callbacks::SuccessNotification scanCompleted,
		Callbacks::Discovered deviceDiscoveredCb, Callbacks::Error failure) {
	return scan(0, scanCompleted, deviceDiscoveredCb, failure);
}


bool BLECentral::startScan(const Service::UUIDList & services,
		Callbacks::SuccessNotification scanCompleted,
		Callbacks::Discovered deviceDiscoveredCb, Callbacks::Error failure) {


	return scan(services, 0, scanCompleted, deviceDiscoveredCb, failure);


}

bool BLECentral::stopScan(Callbacks::SuccessNotification succ,
		Callbacks::Error failure) {
	BLECENTRAL_ENSURE_ADAPTER_AVAIL(failure);
	if (! is_scanning) {

		AsyncAction::Details alreadyDoneAct("stopScanDone", succ, failure);
		alreadyDoneAct.trigger = [](AsyncAction::Details * thisAction) {
			thisAction->completedWithSuccess();
		};
		queueAsyncAction(alreadyDoneAct);
		return true;
	}

	// we are currently scanning, which means we have an async op running


	if (asyncActions.size() && asyncActions.front().isRunning() && asyncActions.front().name == "scan") {
		asyncActions.front().cancelWithoutCallback();
	}



	AsyncAction::Details asyncAct("stopScan", succ, failure);
	asyncAct.trigger = [this](AsyncAction::Details * thisAction) {
		if (gattlib_adapter_scan_disable_async(adapter, clib_scan_disable_done) != 0)
		{
			thisAction->completedWithFailure();
		}

	};


	queueAsyncAction(asyncAct);

#if 0

		callbacks.success = succ;
		callbacks.failure = failure;
		if (gattlib_adapter_scan_disable_async(adapter, clib_scan_disable_done) != 0)
		{

			BLECENTRAL_TRIGGER_CB_IFSET(failure, "scan disable call failed");
		}
#endif

	return true;

}
bool BLECentral::isConnected(const UUID & devId) {
	Device::Details * dev = deviceDetails(devId);
	if (! dev) {
		return false;
	}
	return (dev->connection != NULL);

}

bool BLECentral::connect(const UUID & devUUID, const ConnectionParams & parameters,
		Callbacks::SuccessNotification succ, Callbacks::Error failure) {

	BLECENTRAL_ENSURE_ADAPTER_AVAIL(failure);

	UUID devId = normalizeDeviceUUID(devUUID);

	if (isConnected(devId)) {

		BLECENTRAL_TRIGGER_CB_IFSET(failure, "is already connected");
		return false;
	}

	Device::Details * devDets = deviceDetails(devId);
	if (! devDets) {
		devices[devId].id = devId;
		devDets = deviceDetails(devId);
	}
	connected_to = devId;



	AsyncAction::Details asyncAct("connect", succ, failure);
	asyncAct.trigger = [this, devId, parameters](AsyncAction::Details * thisAction) {

		if (gattlib_async_connect(NULL, devId.c_str(),
							(uint8_t)parameters.destinationType,
							parameters.security,
							parameters.PSM,
							parameters.MTU,
							clib_connected_callback) != 0)
		{

			thisAction->completedWithFailure();
		}


	};


	queueAsyncAction(asyncAct);

#if 0


	callbacks.setup(succ, failure);
	if (gattlib_async_connect(NULL, devId.c_str(),
						(uint8_t)parameters.destinationType,
						parameters.security,
						parameters.PSM,
						parameters.MTU,
						clib_connected_callback) != 0)
	{

		BLECENTRAL_TRIGGER_CB_IFSET(failure, "connect call failed");
		return false;
	}

#endif
	return true;

}

bool BLECentral::connect(const UUID& device,
		Callbacks::SuccessNotification succ, Callbacks::Error failure) {

	return connect(device, connParams, succ, failure);

}

bool BLECentral::disconnect(const UUID& devId,
		Callbacks::SuccessNotification succ, Callbacks::Error failure) {
	BLECENTRAL_ENSURE_ADAPTER_AVAIL(failure);
	if (! isConnected(devId)) {
		BLECENTRAL_TRIGGER_CB_IFSET(failure, "disconnect called, but not connected?");
		return false;
	}

	Device::Details * devDets = deviceDetails(devId);



	AsyncAction::Details asyncAct("disconnect", succ, failure);
	asyncAct.trigger = [devDets](AsyncAction::Details * thisAction) {

		if (gattlib_disconnect_async(devDets->connection, clib_disconnected_callback)) {

			thisAction->completedWithFailure();
		}


	};


	queueAsyncAction(asyncAct);




#if 0

	callbacks.setup(succ, failure);
	reportQueue.push_back([devDets, failure](){

		if (gattlib_disconnect_async(devDets->connection, clib_disconnected_callback)) {

			BLECENTRAL_TRIGGER_CB_IFSET(failure, "disconnect call failed");

		}
	});

#endif
	return true;

}

bool BLECentral::read(const UUID& device, const Service::UUID& service_uuid,
		const Characteristic::UUID& characteristic_uuid,
		Callbacks::IncomingData inData, Callbacks::Error failure) {

	return read(device, characteristic_uuid, inData, failure);
}

bool BLECentral::read(const UUID& device,
		const Characteristic::UUID& characteristic_uuid,
		Callbacks::IncomingData inData, Callbacks::Error failure) {
	BLECENTRAL_ENSURE_ADAPTER_AVAIL(failure);
	if (! isConnected(device)) {
		BLECENTRAL_TRIGGER_CB_IFSET(failure, "read called, not connected");
		return false;
	}

	Device::Details * dets = deviceDetails(device);
	uuid_t char_uuid;
	if (! getUUIDForCharOrFail(dets, characteristic_uuid,
			[](const Characteristic::Details & cd) -> bool {
				return cd.supportsReads();
			},
			&char_uuid, failure))
	{
		return false;
	}


	Characteristic::Details & charDets = dets->characteristic(
					characteristic_uuid);


	AsyncAction::Details asyncAct("read", inData, failure);
	uuid_t * cuuidptr = &char_uuid;
	asyncAct.trigger = [dets, &charDets](AsyncAction::Details * thisAction) {
		if (gattlib_read_char_by_uuid_async(dets->connection, &(charDets.gl_uuid), clib_read_char_callback) != 0)
		{
				thisAction->completedWithFailure();
		}


	};


	queueAsyncAction(asyncAct);
	/*

	if (gattlib_read_char_by_uuid_async(dets->connection, &char_uuid, clib_read_char_callback) != 0)
	{
		BLECENTRAL_TRIGGER_CB_IFSET(failure, "async read call failed");
					return false;
	}
	*/

	return true;

}

void BLECentral::queueAsyncAction(const AsyncAction::Details & dets) {
	BLECNTL_DEBUGLN("Queueing async action " << dets.name);
	asyncActions.push(dets);

}

bool BLECentral::write(const UUID& device, const Service::UUID& service_uuid,
		const Characteristic::UUID& characteristic_uuid,
		const BinaryBuffer& value, Callbacks::SuccessNotification succ,
		Callbacks::Error failure) {
	return write(device, characteristic_uuid, value, succ, failure);
}

bool BLECentral::write(const UUID& device,
		const Characteristic::UUID& characteristic_uuid,
		const BinaryBuffer& value, Callbacks::SuccessNotification succ,
		Callbacks::Error failure) {

	BLECENTRAL_ENSURE_ADAPTER_AVAIL(failure);
	if (!isConnected(device)) {
		BLECENTRAL_TRIGGER_CB_IFSET(failure, "write called, not connected");
		return false;
	}

	Device::Details * dets = deviceDetails(device);
	uuid_t char_uuid;
	if (! getUUIDForCharOrFail(dets, characteristic_uuid,

			[](const Characteristic::Details & cd) -> bool {
							return cd.supportsWrites();
			},

			&char_uuid, failure))
	{
		return false;
	}

	// new buffer -- will be deleted after async call...
	uint8_t * buffer = new uint8_t[value.size()] ;
	if (! buffer )
	{

		BLECENTRAL_TRIGGER_CB_IFSET(failure,
				"could not allocate buffer");
		return false;
	}
	for (BinaryBuffer::size_type i=0; i<value.size(); i++) {
		buffer[i] = value[i];
	}

	BinaryBuffer::size_type buf_size = value.size();

	Characteristic::Details & charDets = dets->characteristic(
					characteristic_uuid);

	AsyncAction::Details asyncAct("write", succ, failure);
	asyncAct.trigger = [dets, &charDets, buffer, buf_size](AsyncAction::Details * thisAction) {

		if (gattlib_write_char_by_uuid_async(dets->connection,
					&(charDets.gl_uuid), buffer, buf_size,
					clib_generic_async_op_done,
					clib_generic_async_op_failed
					) !=0)
			{
				thisAction->completedWithFailure();
			}

		delete [] buffer;

	};

	queueAsyncAction(asyncAct);



#if 0
	callbacks.setup(succ, failure);
	// no async version yet...
	if (gattlib_write_char_by_uuid_async(dets->connection,
			&char_uuid, buffer, value.size(),
			clib_generic_async_op_done,
			clib_generic_async_op_failed
			) !=0)
	{
		delete [] buffer;

		BLECENTRAL_TRIGGER_CB_IFSET(failure,
				"write call failed");
		return false;

	}
	delete[] buffer;

#endif

	// reportQueue.push_back(succ);


	return true;
}


bool BLECentral::writeWithoutResponse(const UUID& device,
		const Service::UUID& service_uuid,
		const Characteristic::UUID& characteristic_uuid,
		const BinaryBuffer& value, Callbacks::SuccessNotification succ,
		Callbacks::Error failure) {
	return writeWithoutResponse(device, characteristic_uuid, value, succ, failure);
}

bool BLECentral::writeWithoutResponse(const UUID& device,
		const Characteristic::UUID& characteristic_uuid,
		const BinaryBuffer& value, Callbacks::SuccessNotification succ,
		Callbacks::Error failure) {
	// TODO:FIXME implement
	return write(device, characteristic_uuid, value, succ, failure);
}

bool BLECentral::startNotification(const UUID& device,
		const Service::UUID& service_uuid,
		const Characteristic::UUID& characteristic_uuid,
		Callbacks::IncomingData inDataCallback, Callbacks::Error failure) {

	// Characteristic::UUID characteristic_uuid = normalizeCharacteristic(chr_uuid);

	BLECNTL_DEBUG("\nAttempting to subscribe to char "<< characteristic_uuid << "... ");
	BLECENTRAL_ENSURE_ADAPTER_AVAIL(failure);
	if (!isConnected(device)) {
		BLECENTRAL_TRIGGER_CB_IFSET(failure,
				"startNotifs called, not connected");
		return false;
	}

	Device::Details * dets = deviceDetails(device);
	uuid_t char_uuid;
	if (!getUUIDForCharOrFail(dets, characteristic_uuid,

	[](const Characteristic::Details & cd) -> bool {
		return cd.supportSubscriptions();
	},

	&char_uuid, failure)) {
		BLECNTL_DEBUGLN("but could not get it's uuid!");
		return false;
	}

	bool shouldRegister = true;
	DEVDETS_LOCKGUARD_BEGINBLOCK(dets, "startNotif");
		if (dets->hasCharacteristic(characteristic_uuid)) {
			if (dets->characteristic(characteristic_uuid).registeredForNotifs) {
				BLECNTL_DEBUGLN("but already registered.");
				shouldRegister = false;
			} else {
				BLECNTL_DEBUGLN("noting registered state.");
				dets->characteristic(characteristic_uuid).registeredForNotifs =
						true;
			}
		}

		dets->setNotificationHandler(characteristic_uuid, inDataCallback);

		if (shouldRegister) {
			if (dets->num_registered_for_notifs) {
				dets->num_registered_for_notifs++;
				BLECNTL_DEBUGLN("now have " << (int)dets->num_registered_for_notifs << " registered listeners.");
			} else {
				BLECNTL_DEBUGLN("first registered char, setting up gattlib notifs");
				// start off by registering our global handler for notif/indications
				void * ho = (void*) (dets->id.c_str());
				gattlib_register_notification(dets->connection,
						clib_notification_handler_callback, ho);
				gattlib_register_indication(dets->connection,
						clib_notification_handler_callback, ho);

				dets->num_registered_for_notifs = 1;
			}

			// now, try to start getting notifs for this guy

			BLECNTL_DEBUGLN("starting notifs for the char");
			if (gattlib_notification_start(dets->connection, &char_uuid) != 0) {

				BLECENTRAL_TRIGGER_CB_IFSET(failure,
						"startNotif notification start failed");
				dets->num_registered_for_notifs--;
				return false;
			}
		}

	DEVDETS_LOCKGUARD_ENDBLOCK(); // end guard block

	return true;
}

bool BLECentral::stopNotification(const UUID& device,
		const Service::UUID& service_uuid, const Characteristic::UUID& chr_uuid,
		Callbacks::SuccessNotification succ, Callbacks::Error failure) {


	BLECENTRAL_ENSURE_ADAPTER_AVAIL(failure);

	Characteristic::UUID characteristic_uuid = chr_uuid; // normalizeCharacteristic(chr_uuid);

	if (!isConnected(device)) {
		BLECENTRAL_TRIGGER_CB_IFSET(failure, "stopNotifs called, not connected");
		return false;
	}

	Device::Details * dets = deviceDetails(device);
	uuid_t char_uuid;
	if (! getUUIDForCharOrFail(dets, characteristic_uuid,

			[](const Characteristic::Details & cd) -> bool {
							return cd.supportSubscriptions();
			},

			&char_uuid, failure))
	{
		return false;
	}

	bool shouldUnRegister = true;
	DEVDETS_LOCKGUARD_BEGINBLOCK(dets, "stopNotifs");

		if (dets->hasCharacteristic(characteristic_uuid)) {
			if (! dets->characteristic(characteristic_uuid).registeredForNotifs) {
				shouldUnRegister = false;
			} else {
				dets->characteristic(characteristic_uuid).registeredForNotifs = false;
			}
		}

		if (shouldUnRegister) {
			if (dets->num_registered_for_notifs)
			{
				dets->num_registered_for_notifs--;
				if (dets->num_registered_for_notifs == 0) {
					gattlib_register_notification(dets->connection,
											NULL, NULL);
					gattlib_register_indication(dets->connection,
											NULL, NULL);
				}
			}

			if ( gattlib_notification_stop(dets->connection, &char_uuid) != 0)
			{

				BLECENTRAL_TRIGGER_CB_IFSET(failure,
						"stopNotif notification_stop call failed");
				return false;
			}
		}
	DEVDETS_LOCKGUARD_ENDBLOCK();

	if (succ) {
		reportQueue.push_back(succ);
	}
	return true;



}

bool BLECentral::isConnected(const UUID& device,
		Callbacks::SuccessNotification succ, Callbacks::Error failure) {
	BLECENTRAL_ENSURE_ADAPTER_AVAIL(failure);
	if (isConnected(device)) {

		reportQueue.push_back(succ);
	} else {
		reportQueue.push_back(failure);
	}
	return true;
}

bool BLECentral::isEnabled(Callbacks::SuccessNotification succ, Callbacks::Error failure) {

	BLECENTRAL_ENSURE_ADAPTER_AVAIL(failure);
	reportQueue.push_back(succ);

	return true;
}

bool BLECentral::enable(Callbacks::SuccessNotification succ,
		Callbacks::Error failure) {

	BLECENTRAL_ENSURE_ADAPTER_AVAIL(failure);

	if (gattlib_adapter_powered(adapter) ) {

		reportQueue.push_back(succ);
	} else {
		BLECNTL_DEBUGLN("Adapter is available but NOT powered...");
		reportQueue.push_back(failure);
	}

	return true;

}



/* **************** internals/public -- used by C callbacks ************ */
void BLECentral::readDataReceived(const uint8_t * buf, size_t len) {
	BinaryBuffer binBuf;


	if (! asyncActions.size()) {

		BLECNTL_ERRORLN("got readDataReceived() but no async actions in Q?");
		return;
	}

	AsyncAction::Details & curAct = asyncActions.front();
	if (curAct.callbacks.datareceived) {

		binBuf.insert(binBuf.end(), buf, &(buf[len]));

#ifdef BLECENTRAL_FAKE_READASYNC
		Callbacks::IncomingData drcb = curAct.callbacks.datareceived;
		reportQueue.push_back([binBuf, drcb]() {
			drcb(binBuf);
		});

#else
		(curAct.callbacks.datareceived)(binBuf);
#endif

	}
	// this asyn action is done.
	curAct.markCompleted();

#if 0
	if (callbacks.datareceived) {

		binBuf.insert(binBuf.end(), buf, &(buf[len]));
		/*
		for (size_t i=0; i<len; i++) {
			binBuf.push_back(buf[i]);
		}
		*/

		drcb = callbacks.datareceived;
#ifdef BLECENTRAL_FAKE_READASYNC
		reportQueue.push_back([binBuf, drcb]() {
			drcb(binBuf);
		});

#else
		(callbacks.datareceived)(binBuf);
#endif
	}
#endif


}


void BLECentral::deviceDiscovered(const Discovery::Device & dev) {
	namesCache[dev.id] = dev.name;
	if (devDiscoveredCb) {
		(devDiscoveredCb)(dev);
	}
}

void BLECentral::scanCompleted() {

	is_scanning = false;
	currentOpCompleted();

}


void BLECentral::scanDisableCompleted() {
	is_scanning = false;
	currentOpCompleted();

}

bool BLECentral::performServiceDiscovery(Device::Details * onDevice) {
	char uuid_str[BLECENTRAL_UUIDSTRING_MAX_LENGTH + 1];
	int i;
	gattlib_primary_service_t * services;
	int services_count;

	if (gattlib_discover_primary(onDevice->connection, &services,
			&services_count) != 0) {

		BLECNTL_ERRORLN("Failed to discover services");
		return false;
	}

	DEVDETS_LOCKGUARD_BEGINBLOCK(onDevice, "performServDisc");
	onDevice->clearServices();

	for (i = 0; i < services_count; i++) {

		if (gattlib_uuid_to_string(&(services[i].uuid), uuid_str,
		BLECENTRAL_UUIDSTRING_MAX_LENGTH) == 0) {
			BLECNTL_DEBUGLN("Adding service " << uuid_str);

			onDevice->addService(uuid_str, services[i]);
		} else {
			BLECNTL_ERRORLN("Could not convert char uuid to str??");
		}
	}
	DEVDETS_LOCKGUARD_ENDBLOCK();

	free(services);

	return true;
}

bool BLECentral::performCharacteristicsDiscovery(Device::Details * onDevice) {
	gattlib_characteristic_t* characteristics;
	int i, characteristics_count;
	char uuid_str[BLECENTRAL_UUIDSTRING_MAX_LENGTH + 1];


	if (gattlib_discover_char(onDevice->connection, &characteristics,
			&characteristics_count) != 0) {
		BLECNTL_ERRORLN("Failed to discover characteristics");

		return false;
	}

	DEVDETS_LOCKGUARD_BEGINBLOCK(onDevice, "performCharDisc");
	onDevice->clearCharacteristics();
	for (i = 0; i < characteristics_count; i++) {
		if (gattlib_uuid_to_string(&characteristics[i].uuid, uuid_str,
		BLECENTRAL_UUIDSTRING_MAX_LENGTH) == 0) {
			BLECNTL_DEBUGLN("Adding characteristic " << uuid_str);

			onDevice->addCharacteristic(uuid_str, characteristics[i]);
		} else {
			BLECNTL_ERRORLN("Could not convert char uuid to str??");
		}

	}
	DEVDETS_LOCKGUARD_ENDBLOCK();
	free (characteristics);

	return true;
}
bool BLECentral::performDiscovery(Device::Details * onDevice) {

	if (onDevice->discovery_done) {
		BLECNTL_DEBUGLN("Discovery already done");
		return true;
	}
	if ( ! performServiceDiscovery(onDevice)) {
		return false;
	}

	if (! performCharacteristicsDiscovery(onDevice)) {
		return false;
	}

	onDevice->discovery_done = true;
	return true;

}


Service::List BLECentral::servicesFor(const UUID & device) {
	Service::List retList;

	Device::Details * dets = deviceDetails(device);

	if (! (dets && dets->discovery_done) ) {
		return retList;
	}

	for (Device::ServicesMap::const_iterator iter = dets->services.begin();
			iter != dets->services.end();
			iter++)
	{
		const Service::Details & sd = (*iter).second;
		retList.push_back(sd);
	}

	return retList;


}
Characteristic::List BLECentral::characteristicsFor(const UUID & device) {
	Characteristic::List retList;
	Device::Details * dets = deviceDetails(device);

	if (! (dets && dets->discovery_done) ) {
		return retList;
	}

	for (Device::CharacteristicsMap::const_iterator iter = dets->characteristics.begin();
			iter != dets->characteristics.end();
			iter++)
	{
		const Characteristic::Details & cd = (*iter).second;
		retList.push_back(cd);
	}

	return retList;
}

void BLECentral::autoDiscoverServicesStep(Device::Details * onDevice)
{

	BLECNTL_DEBUGLN("doing service discovery, yeah");
	performServiceDiscovery(onDevice);
	reportQueue.push_back([this, onDevice](){
		autoDiscoverCharacteristicsStep(onDevice);
	});

}

void BLECentral::autoDiscoverCharacteristicsStep(Device::Details * onDevice) {
	BLECNTL_DEBUGLN("doing char discovery, yeah");
	performCharacteristicsDiscovery(onDevice);

	onDevice->discovery_done = true;
	reportQueue.push_back([this]() {
		BLECNTL_DEBUGLN("Calling dev conn'ed cb");
		if (asyncActions.size())
		{
			asyncActions.front().completedWithSuccess();
		}
	});
}

void BLECentral::deviceConnected(gatt_connection_t* connection) {
	Device::Details * dets = deviceDetails(connected_to);

	BLECNTL_DEBUGLN("Connected!");
	dets->connection = connection;
	if (dets->connection) {
		if (auto_discover) {
			BLECNTL_DEBUGLN("Will auto discover...");
			// we break up the discovery into multiple steps, as
			// these are synchronous and potentially slow
			reportQueue.push_back([this, dets](){
				// discover services, the push
				autoDiscoverServicesStep(dets);
			});
		} else {
			currentOpCompleted();
		}

	} else {
		BLECNTL_DEBUGLN("deviceConnected() callback called with empty conn");
		if (asyncActions.size()) {
			asyncActions.front().completedWithFailure();
		}

	}

}


void BLECentral::deviceDisconnected() {
	Device::Details * dets = deviceDetails(connected_to);
	if (dets) {
		dets->connection = NULL;
	}
	connected_to = "";
	currentOpCompleted();
}
void BLECentral::currentOpCompleted() {
	
	BLECNTL_DEBUGLN("BLECentral::currentOpCompleted()");
	if (asyncActions.size()) {
		BLECNTL_DEBUGLN("calling completedWithSuccess");
		asyncActions.front().completedWithSuccess();
		BLECNTL_DEBUGLN("done");
	}

}

void BLECentral::currentOpFailed() {
	if (asyncActions.size()) {
		asyncActions.front().completedWithFailure();
	}

}


void BLECentral::handleNotification(const Characteristic::UUID & chr_uuid,
							const uint8_t* data,
							size_t data_length) {

	Callbacks::IncomingNotification notifHandler;

	Characteristic::UUID charUUID = chr_uuid; // normalizeCharacteristic(chr_uuid);
	BLECNTL_DEBUGLN("BLECentral::handleNotification()");
	for (DeviceMap::iterator devIter = devices.begin(); devIter != devices.end(); devIter++) {
		Device::Details & dets = (*devIter).second;

		DEVDETS_LOCKGUARD_BEGINBLOCK((&dets), "handleNotif");
		if (dets.hasNotificationHandlerFor(charUUID)) {

				notifHandler = dets.notificationHandler(charUUID);

				BLECNTL_DEBUGLN("calling handler for " << charUUID);

				BinaryBuffer notifBuf;
				notifBuf.insert(notifBuf.end(), data, &data[data_length]);
				/*
				for (size_t i=data_length; i > 0; i--) {
					notifBuf.push_back(data[i-1]);
				}
				*/
				// std::reverse_copy( &data[data_length], data, std::back_inserter(notifBuf));
				reportQueue.push_back([notifHandler, notifBuf]() {

					notifHandler(notifBuf);
				});

		}

		DEVDETS_LOCKGUARD_ENDBLOCK();
	}
	/*
	devices.find(devId);
		if (iter == devices.end())
		{
			return NULL;
		}

		return &((*iter).second);
	Device::Details * dets = deviceDetails("23");
	if (! dets) {
		BLECNTL_ERRORLN("notif handler could not locate device '" << deviceId << "'");
		return;
	}
	*/


}






const DeviceName & BLECentral::deviceName(const UUID & devUUID) {
	return namesCache[devUUID];
}



BLECentral::BLECentral() : adapter(NULL), adapter_name(""),
		adapter_is_open(false),
		is_scanning(false),
		auto_discover(BLECENTRAL_AUTODISCOVER_ON_CONNECT_DEFAULT)
{


}

BLECentral::~BLECentral() {
	if (connected_to.size()) {
		BLECNTL_DEBUGLN("Attempting auto-disconn on destruct");
		Device::Details * dets = deviceDetails(connected_to);
		if (dets) {
			this->disconnect(dets->id, [](){
				BLECNTL_DEBUGLN("DISCONNECTED!");
			});

			for (uint8_t i=0; i<20; i++) {
				this->processAsync();

			}
		}

	}
}

BLECentral * BLECentral::getInstance() {
	if (ble_central_singleton) {
		return ble_central_singleton;
	}
	ble_central_singleton = new BLECentral();
	return ble_central_singleton;

}
} /* namespace Gattlibpp */
