#!/usr/bin/env python3
# encoding: utf-8
import glob
import os
from operator import itemgetter

def main():
    '''
    Collects all .ris citation files from the publications folder
    and generates a Publications.md in the wiki folder
    containing all important information.
    '''

    #Collect .ris files
    ris_files = []
    for ris in glob.glob(
        os.path.join(
            'publications',
            '**',
            '*.ris'   
        ),
        recursive=True
    ):
        ris_files.append(ris)

    #Extract information from ris files
    #and store it in a dictionary
    publications_dict = {}
    for fullpath in ris_files:
        head, ris = os.path.split(fullpath)
        subfolder = os.path.basename(head)
        if subfolder not in publications_dict.keys():
            publications_dict[subfolder] = {}
        publications_dict[subfolder][ris] = {
            'Authors': []
        }
        with open(fullpath, 'r') as in_file:
            for line in in_file:
                l = line.strip()
                if l.startswith('A1') is True or l.startswith('AU') is True:
                    publications_dict[subfolder][ris]['Authors'].append(
                        l.split('  - ')[1]
                    )
                elif l.startswith('T1') is True:
                    publications_dict[subfolder][ris]['Title'] = l.split('  - ')[1]
                elif l.startswith('Y1') is True or l.startswith('DA') is True:
                    year = int(l.split('  - ')[1].split('/')[0])
                    publications_dict[subfolder][ris]['Year'] = year
                elif l.startswith('JO') is True or l.startswith('JF') is True:
                    publications_dict[subfolder][ris]['Journal'] = l.split('  - ')[1]
                elif l.startswith('VL') is True:
                    publications_dict[subfolder][ris]['Volume'] = l.split('  - ')[1]
                elif l.startswith('IS') is True:
                    publications_dict[subfolder][ris]['Issue'] = l.split('  - ')[1]
                elif l.startswith('UR') is True:
                    publications_dict[subfolder][ris]['URL'] = l.split('  - ')[1]
                elif l.startswith('N2') is True or l.startswith('AB') is True:
                    publications_dict[subfolder][ris]['Abstract'] = l.split('  - ')[1]

    #Write markdown file for wiki
    #based on info in dict
    output_filename = os.path.join(
        'wiki',
        'Publications.md'
    )
    with open(output_filename, 'w') as out_file:
        print('# Publications [ ](# )', file=out_file)
        print('', file=out_file)
        for subheading in sorted(publications_dict.keys()):
            print(' * [{0}](#{1})'.format(
                subheading.replace ('_', ' '),
                subheading.replace(' ', '-').lower()
            ), file=out_file)
        print('', file=out_file)
        for subheading in sorted(publications_dict.keys()):
            print('## {0}'.format(subheading.replace ('_', ' ')), file=out_file)
            print('', file=out_file)
            pub_list = []
            for pub in publications_dict[subheading].keys():
                citation_file = 'https://github.com/halophiles/halowiki/publications/{0}/{1}'.format(
                    subheading,
                    pub
                )
                publications_dict[subheading][pub]['Citation'] = citation_file
                publications_dict[subheading][pub]['Lead Author'] = publications_dict[subheading][pub]['Authors'][0]
                pub_list.append(publications_dict[subheading][pub])
            for pub in sorted(
                pub_list,
                key=itemgetter('Year', 'Lead Author'),
                reverse=True,
            ):
                print(
'''*{0}*
{1}
**{2}**
{3} {4}({5})
<details>
<summary>Abstract and Links</summary>
[Link to Publication]({6})
[Citation]({7})
{8}
</details>
'''.format(
                pub['Title'],
                '; '.join(pub['Authors']),
                pub['Year'],
                pub['Journal'],
                pub['Volume'],
                pub['Issue'],
                pub['URL'],
                pub['Citation'],
                pub['Abstract'],
                ), file=out_file)

            print(
'''[Go to top of page](# )
----''',
                file=out_file
            )

if __name__ == '__main__':
    main()