import struct
from twisted.internet.protocol import Protocol, ClientFactory

class PeerProtocol(Protocol):
    '''
    An instance of the BitTorrent protocol. This serves as a client.
    '''

    def __init__(self):
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False
        self.handshaked = False
        self.timer = None
 
    def connectionMade(self):
        self.handshake()
        self.self_unchoke()
        self.self_interested()

    def dataReceived(self, data):
        if not self.handshaked:
            self.decode_handshake(data)
        else:
            len_prefix, msg_id = self.deocde_len_id(data)
            #TODO
    
    def self_keep_alive(self):
        self.transport.write(struct.pack('!I', 0))

    def self_choke(self):
        self.transport.write(struct.pack('!IB', 1, 0))
        self.am_choking = True

    def self_unchoke(self):
        self.transport.write(struct.pack('!IB', 1, 1))
        self.am_choking = False

    def self_interested(self):
        self.transport.write(struct.pack('!IB', 1, 2))
        self.am_interested = True

    def self_uninterested(self):
        self.transport.write(struct.pack('!IB', 1, 3))
        self.am_interested = False

    def keep_alive(self):
        pass

    def choke(self):
        self.peer_choking = True

    def unchoke(self):
        self.peer_choking = False

    def interested(self):
        self.peer_interested = True

    def uninterested(self):
        self.peer_interested = False

    def decode_len_id(self, message):
        len_prefix = struct.unpack_from('!I', message)
        if not len_prefix: #keep alive message, ID is None
            return (0, None)
        else:
            message_id = ord(message[4]) #single byte that must be the 5th byte
            return (len_prefix, message_id)

    def encode_len_id(self, len_prefix, message_id):
        if not len_prefix: #keep alive message
            return '\x00\x00\x00\x00'
        else:
            return struct.pack('!IB', len_prefix, message_id)

    def handshake(self):
        peer_id = self.factory.client.client_id
        info_hash = self.factory.torrent.info_hash
        reserved = chr(0) * 8
        pstr = 'BitTorrent protocol'
        pstrlen = 68

        handshake_msg = pstrlen + pstr + reserved + info_hash + peer_id
        self.transport.write(handshake_msg)

    def decode_handshake(self, data):
        '''
        Verify that our peer is sending us a well formed handshake, if not
        we then raise an errback that will close the connection. We can't check
        against peer_id because we set the compact flag in our tracker request.
        If the handshake is well formed we set the handshaked instance variable
        to True so that we know to accept further messages from this peer.
        '''

        try:
            if ord(data[0]) != 68:
                #WE NEED TO BREAK OUT TODO, some kind of errback
                pass
            elif data[28:48] != self.factory.torrent.info_hash:
                #WE NEED TO BREAK OUT TODO, some kind of errback
                pass
            elif data[1:20] != 'BitTorrent protocol':
                #WE NEED TO BREAK OUT TODO, some kind of errback
                pass
        except IndexError:
            #WE NEED TO BREAK OUT TODO, some kind of errback
            pass

        self.handshaked = True

    def _payload(self, message):
        '''Convenience method to extract payload'''
        return message[5:]

class PeerProtocolFactory(ClientFactory):
    '''
    Factory to generate instances of the Peer protocol. A Twisted concept.
    '''

    protocol = PeerProtocol

    def __init__(self, client, torrent):
        self.client = client
        self.torrent = torrent

    def clientConnectionLost(self, connector, reason):
        pass
        #need to pass this up to the controlling torrent

    def clientConnectionFailed(self, reason):
        pass
