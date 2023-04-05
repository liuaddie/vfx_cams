import os
from pyftpdlib import servers
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.authorizers import DummyAuthorizer

def main():
    root_folder = 'ftp'
    if not os.path.exists(root_folder):
        os.makedirs(root_folder)
    authorizer = DummyAuthorizer()
    authorizer.add_user('photogrammetry', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('B001', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('B002', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('B003', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('B004', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('B005', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('B006', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('B007', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('B008', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('B009', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('B010', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('B011', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('B012', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('C001', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('C002', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('C003', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('C004', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('C005', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('C006', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('C007', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('C008', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('C009', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('C010', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('C011', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('C012', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('C013', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('D001', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('D002', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('D003', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('E001', 'Addie123', root_folder, perm='elradfmwM')
    authorizer.add_user('E002', 'Addie123', root_folder, perm='elradfmwM')
    handler = FTPHandler
    handler.authorizer = authorizer
    address = ("0.0.0.0", 21)  # listen on every IP on my machine on port 21
    server = servers.FTPServer(address, handler)
    server.serve_forever()

if __name__ == '__main__':
    main()
