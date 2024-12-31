if __name__ == '__main__':
    csv_fn = "Wemo-Mini-Smart-Plug--WiFi-Enabled--Works-with-Alexa--Google-Assistant-&-Apple-HomeKit.csv"
    with open('./data/' + csv_fn, 'r', encoding='utf-8') as input_file, open('./data/RM--' + csv_fn, 'a',
                                                                             encoding='utf-8') as output_file:
        seen = set()
        for line in input_file:
            if line in seen:
                continue

            seen.add(line)
            output_file.write(line)
    input_file.close()
    output_file.close()
    print("Duplications Removed.")
