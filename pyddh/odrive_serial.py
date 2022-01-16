import odrive

if __name__ == '__main__':
    odv = odrive.find_any()
    print('ODrive Found')
    print('Serial Number: %s' % format(odv.serial_number, 'X'))
