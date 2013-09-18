# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+
import logging
import bz2
import uuid
import time
import dateutil.parser
from lxml import etree
from base64 import b64decode

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Import.AbstractImporter import AbstractImporter
from netzob.Common.Models.L4NetworkMessage import L4NetworkMessage


class UsbHexImporter(AbstractImporter):

    def __init__(self, netzob):
        super(UsbHexImporter, self).__init__("USBHEX IMPORT", netzob)
        self.log = logging.getLogger(__name__)
        self.filesToBeImported = []

    def setSourceFiles(self, filePathList):
        self.filesToBeImported = filePathList

    def readMessages(self):
        self.messages = []
        for filePath in self.filesToBeImported:
            currentFileMessageList = self._parseUsbHexFile(filePath)
            self.messages.extend(currentFileMessageList)

    def _parseUsbHexFile(self, filePath):
        data = self._readFile(filePath)
        self.log.debug("Loaded file in memory")
                
        return self._extractMessagesFromUsbHex(data)

    def _extractMessagesFromUsbHex(self, data):
        logging.info("extracting USB messages...")
        messages = []
        
        logging.debug("Load the line structure in memory")
        
        for line in data.split('\n'):
            message = self.extractMessageFromLine(line)
            if message != None:
                messages.append(message)
            
        return messages

    def extractMessageFromLine(self, line):
        if line == None:
            return None
        elements = line.split(',')
        if len(elements) != 2:
            logging.warning("invalid line format: " + line)
            return
        
        id = str(uuid.uuid4())
        
        timestamp = 1379562792
        msg_data = elements[1]
        direction = elements[0]        
        data = None
        
        # Retrieves the data of the message
        if msg_data != None:
            data = "".join(msg_data.split()).lower()
        logging.info("Data read back as: " + data)
        if data != None:
            if direction == "in":
                ip_source = "127.0.0.1"
                ip_destination = "127.0.0.2"
            else:
                ip_source = "127.0.0.2"
                ip_destination = "127.0.0.1"
            protocol = "usb"
            source_port = "80"
            destination_port = "80"

            message = L4NetworkMessage(id, timestamp, data,
                                       None, None, None,
                                       "IP", ip_source, ip_destination,
                                       protocol, source_port, destination_port)
            return message

    def _readFile(self, path):
        logging.debug("Read the provided File.")
        file = open(path, "r")
        data = file.read()
        file.close()
        return data
