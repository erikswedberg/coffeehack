# -*- coding: utf-8 -*-
"""
    fontcatalog.manage.cldr
    ~~~~~~~~~~~~~~~~~~~~~

    cldr management commands
"""

from flask import current_app, jsonify
from flask.ext.script import Command, prompt, prompt_pass
import os, subprocess, json, tempfile, time, zipfile, shutil
from ..helpers import UnicodeReader, json_minify, SanitizeURLName

#from ..models import City, Citydata
from .. import db


'''
def ImportAppleLanguageMetadata(apple_dir, data):
    
    #pull stuff out of metadata
    json_file = open(apple_dir+'/apple-languages.json')

    #json_minify pulls comments out of JSON and reads in valid data
    json_data = json.loads(json_minify(json_file.read()))
        
    if 'appleData' in json_data and 'languages' in json_data['appleData']:
        for json_language in json_data['appleData']['languages']:
            if 'cldrLanguageId' in json_language:
                language_id = json_language['cldrLanguageId']
                if language_id in data['languages'] and isinstance(data['languages'][language_id], Language):
                    if 'alphabet' in json_language:
                        data['languages'][language_id].alphabet = json_language['alphabet']
                    if 'specimen' in json_language:
                        data['languages'][language_id].specimen = json_language['specimen']
                    if 'samples' in json_language:
                        data['languages'][language_id].samples = json_language['samples']
                    if 'pangrams' in json_language:
                        data['languages'][language_id].pangrams = json_language['pangrams']
    json_file.close()
    
    return data

def ImportAppleScriptMetadata(apple_dir, data):
    
    #pull stuff out of metadata
    json_file = open(apple_dir+'/apple-scripts.json')

    #json_minify pulls comments out of JSON and reads in valid data
    json_data = json.loads(json_minify(json_file.read()))
        
    if 'appleData' in json_data and 'scripts' in json_data['appleData']:
        for json_script in json_data['appleData']['scripts']:
            if 'name' in json_script and 'cldrScriptId' in json_script:
            
                script_name = json_script['name']
                script_id = json_script['cldrScriptId']
                if script_id in data['scripts'] and isinstance(data['scripts'][script_id], Script):
                    if data['scripts'][script_id].name_en != script_name:
                        data['scripts'][script_id].name_apple = script_name
                        data['scripts'][script_id].url_name = SanitizeURLName(script_name)
                        
    json_file.close()
    
    return data

def ImportCldrMetadata(cldr_dir, data):
    
    #pull stuff out of metadata
    json_file = open(cldr_dir+'/json-full/supplemental/metadata.json')
    json_data = json.load(json_file)
    source = 'cldr '+json_data['supplemental']['version']['_cldrVersion']
    
    metadata_vars = json_data['supplemental']['metadata']['validity']
    for metadata_var in metadata_vars:
        if 'variable' in metadata_var:
            if metadata_var['variable']['_id'] == '$language':
                llist = metadata_var['variable']['_value'].split()    
                for l in llist:
                    if not l in data['languages']:
                        data['languages'][l] = Language(id=l, source=source)
            if metadata_var['variable']['_id'] == '$script':
                slist = metadata_var['variable']['_value'].split()    
                for s in slist:
                    if not s in data['scripts']:
                        data['scripts'][s] = Script(id=s, source=source)
            if metadata_var['variable']['_id'] == '$territory':
                tlist = metadata_var['variable']['_value'].split()    
                for t in tlist:
                    if not t in data['territories']:
                        data['territories'][t] = Territory(id=t, source=source)
     
    json_file.close()
    return data

def ImportCldrMetadataLocales(cldr_dir, data):

    #pull stuff out of metadata
    json_file = open(cldr_dir+'/json-full/supplemental/metadata.json')
    json_data = json.load(json_file)
    source = 'cldr '+json_data['supplemental']['version']['_cldrVersion']

    locale_string = json_data['supplemental']['metadata']['defaultContent']['_locales']
    locale_list = locale_string.split()
    for loc in locale_list:
        #if not loc in data['locales']:
        if not loc in data['languages']:
            loc_lang_id = loc.split('-')[0]
            if loc_lang_id in data['languages']:
                data['locales'][loc] = Locale(id=loc, language_id=loc_lang_id, source=source)

    json_file.close()
    return data
    
def ImportCldrLanguageNames(cldr_dir, data):
    
    #pull stuff out of languages.json
    json_file = open(cldr_dir+'/json-full/main/en-US/languages.json')
    json_data = json.load(json_file)
    source = 'cldr '+json_data['main']['en-US']['identity']['version']['_cldrVersion']
    
    language_vars = json_data['main']['en-US']['localeDisplayNames']['languages']
    for id, name in language_vars.iteritems():
        if not id in data['languages']:
            #ones that weren't found in the previous import
            #print '*** not found *** '+id+' '+name
            
            #handle the case if we come across something like "ky-alt-variant": "Kirghiz" or "en-GB-alt-short": "U.K. English"
            id_list = id.split('-')
            if len(id_list) > 1 and id_list[1] == 'alt':
                if id_list[0] in data['languages']:
                    data['languages'][id_list[0]].name_alt = name
            elif len(id_list) > 2 and id_list[2] == 'alt':        
                if id_list[0]+'-'+id_list[1] in data['languages']:
                    data['languages'][id_list[0]+'-'+id_list[1]].name_alt = name                    
            else:
                data['languages'][id] = Language(id=id, name_en=name, url_name=SanitizeURLName(name), source=source)
        else:
            data['languages'][id].name_en = name
            data['languages'][id].url_name = SanitizeURLName(name)

    json_file.close()
    return data

def ImportCldrScriptNames(cldr_dir, data):
    
    #pull stuff out of scripts.json
    json_file = open(cldr_dir+'/json-full/main/en-US/scripts.json')
    json_data = json.load(json_file)
    source = 'cldr '+json_data['main']['en-US']['identity']['version']['_cldrVersion']
    
    script_vars = json_data['main']['en-US']['localeDisplayNames']['scripts']
    for id, name in script_vars.iteritems():
        if not id in data['scripts']:
            #ones that weren't found in the previous import
            #print '*** not found *** '+id+' '+name
            id_list = id.split('-')
            if len(id_list) > 1 and id_list[1] == 'alt':
                if id_list[0] in data['scripts']:
                    data['scripts'][id_list[0]].name_alt = name
            else:
                data['scripts'][id] = Script(id=id, name_en=name, url_name=SanitizeURLName(name), source=source)
        else:
            data['scripts'][id].name_en = name
            data['scripts'][id].url_name = SanitizeURLName(name)
                
    json_file.close()
    return data

def ImportCldrTerritoryNames(cldr_dir, data):
    
    #pull stuff out of territories.json
    json_file = open(cldr_dir+'/json-full/main/en-US/territories.json')
    json_data = json.load(json_file)
    source = 'cldr '+json_data['main']['en-US']['identity']['version']['_cldrVersion']
    
    territory_vars = json_data['main']['en-US']['localeDisplayNames']['territories']
    for id, name in territory_vars.iteritems():
        if not id in data['territories']:
            #ones that weren't found in the previous import
            #print '*** not found *** '+id+' '+name
            
            #handle the case if we come across something like "ky-alt-variant": "Kirghiz" or "en-GB-alt-short": "U.K. English"
            id_list = id.split('-')
            if len(id_list) > 1 and id_list[1] == 'alt':
                if id_list[0] in data['territories']:
                    data['territories'][id_list[0]].name_alt = name
            else:
                data['territories'][id] = Territory(id=id, name_en=name, source=source)
        else:
            data['territories'][id].name_en = name    
    
    json_file.close()
    return data
            
def ImportCldrTerritoryInfo(cldr_dir, data):
    
    #pull stuff out of territoryInfo.json
    json_file = open(cldr_dir+'/json-full/supplemental/territoryInfo.json')
    json_data = json.load(json_file)
    
    territory_vars = json_data['supplemental']['territoryInfo']
    for id, tdict in territory_vars.iteritems():
        if id in data['territories']:
            if '_gdp' in tdict:
                data['territories'][id].gdp = tdict['_gdp']
            if '_literacyPercent' in tdict:
                data['territories'][id].literacy_percent = tdict['_literacyPercent']
            if '_population' in tdict:
                data['territories'][id].population = tdict['_population']
            if 'languagePopulation' in tdict:
                for loc, ldict in tdict['languagePopulation'].iteritems():

                    official_status = None
                    population_percent = None
                    writing_percent = None
                    if '_officialStatus' in ldict:
                        official_status = ldict['_officialStatus']
                    if '_populationPercent' in ldict:
                        population_percent = ldict['_populationPercent']
                    if '_writingPercent' in ldict:
                        writing_percent = ldict['_writingPercent']

                    loc = loc.replace('_', '-')
                    #print loc+' '+data['territories'][id].id
                    if loc in data['languages']:
                        #a = Language2Territory(official_status=official_status,population_percent=population_percent,writing_percent=writing_percent)
                        #a.territory = data['territories'][id]
                        #data['languages'][loc].territories.append(a)
                        a = Language2Territory(language_id=data['languages'][loc].id,\
                                           territory_id=data['territories'][id].id,\
                                           official_status=official_status,\
                                           population_percent=population_percent,\
                                           writing_percent=writing_percent)
                        data['language2territories'][a.language_id+'_'+a.territory_id] = a
                    elif loc in data['locales']:
                        a = Locale2Territory(locale_id=data['locales'][loc].id,\
                                           territory_id=data['territories'][id].id,\
                                           official_status=official_status,\
                                           population_percent=population_percent,\
                                           writing_percent=writing_percent)
                        data['locale2territories'][a.locale_id+'_'+a.territory_id] = a
                        ##a = Locale2Territory(official_status=official_status,population_percent=population_percent,writing_percent=writing_percent)
                        #a.territory = data['territories'][id]
                        #data['locales'][loc].territories.append(a)
                    else:
                        pass
                        #there are lots of languages in this list that aren't found
                        #so i went back in time and imported them from iso639
                        #rkt, grt, ccp, syl, wls, fud, ms-Arab, lep, tsj, gub, kgp, xav, koi, mrj, lbe, rcf, bvb, ryu, gcr, syl, puu, man-Nkoo, man-Latn, saf, abr, btv, khw, brh, sd-Arab,
                        # skr, bft, kxp, kvx, hnd, mvy, gju, tg-Arab, hno, gjk, bhk, mdh, tbw, hnn, tsg, bku, bto, cjm, ndc, kck, mxc, gag, rif, kht, mnw, dtm, kao, ffm, bze, bmq, mwk,
                        # kk-Arab, ug-Cyrl, laj, myx, ttj, mgy, zmi, bjn, nhe, maz, nch, nhw, yua, rmf, uli, zea, rif, gos, fuq, fuv, amo, ha-Arab, pcm, tkt, lif-Deva, taj, tsf, gvr, tdh,
                        # rjs, tdg, lep, unr-Deva, mgp, jml, ggn, bfy, xsr, bap, thr, thq, thl, mrd, bci, dnj, bqv, sef, lmo, rmo, nxq, lcp, tdd, kk-Arab, ky-Arab, lis, khb, mn-Mong, ha-Arab,
                        # ms-Arab, ikt, scs, atj, nsk, cr-Cans, moe, crj, crk, csw, crl, crm, vic, pko, kdt, cja, zdj, kri, crs, ug-Cyrl, fit, rmu, ha-Arab, buc, ku-Arab, kdt, kjg,
                        # ky-Latn, bgx, mfa, kxm, lcp, nod, mnw, tts, sou, lwl, kdt, prd, kk-Arab, haz, prd, glk, lrc, rmt, luz, lki, kk-Arab, bqi, az-Arab, sdh, bhi, btv, kfr, bhb, 
                        # kht, bjj, rkt, kfy, unx-Beng, khn, xnr, gon-Telu, grt, sd-Arab, hoc, sck, sd-Deva, tcy, hoj, wtm, wbr, bfq, unr-Beng, bft, bfy, ria, swv, lif-Deva, noe, dcc,
                        # lep, lmn, wbq, srx, saz, bgc, hne, mtr, gbm, ccp, lbw, bjn, rob, sxn, kvr, bbc, aoz, rej, ms-Arab, nij, kge, ljp, bya, bew, rue, ngl, ndc, rng, vmw
                        #print '** not found **'+loc+' '+data['territories'][id].id

    json_file.close()
    return data            

def ImportCldrLanguageData(cldr_dir, data):

    #pull stuff out of territoryInfo.json
    json_file = open(cldr_dir+'/json-full/supplemental/languageData.json')
    json_data = json.load(json_file)
    
    language_vars = json_data['supplemental']['languageData']
    for id, ldict in language_vars.iteritems():
        importance = 'primary'
        if '-alt-secondary' in id:
            id = id.replace('-alt-secondary', '')
            importance = 'secondary'
        if id in data['languages']:
            if '_scripts' in ldict:
                for script in ldict['_scripts']:
                    if script in data['scripts']:
                        a = Language2Script(language_id=id,\
                                           script_id=script,\
                                           importance=importance)
                        data['language2scripts'][a.language_id+'_'+a.script_id] = a
                    else:
                        #script not found
                        pass
            if '_territories' in ldict:
                for territory in ldict['_territories']:
                    if territory in data['territories']:
                        if (id+'_'+territory) in data['language2territories']:
                            l2t = data['language2territories'][id+'_'+territory]
                            l2t.importance = importance
                        else:
                            a = Language2Territory(language_id=id,\
                                               territory_id=territory,\
                                               importance=importance)
                            data['language2territories'][a.language_id+'_'+a.territory_id] = a
                    else:
                        print territory
        else:
            #no locale2scripts
            pass
            
    json_file.close()
    return data
            
def ImportCldrLocalLanguageNames(cldr_dir, data):            
            
    #go through ~709 subdirectories in /main
    for f in os.listdir(cldr_dir+'/json-full/main'):
        (filepath, filename) = os.path.split(f)

        json_file = open(cldr_dir+'/json-full/main/'+filename+'/languages.json')
        json_data = json.load(json_file)
        if filename in json_data['main']:
            locale_key = filename

            language_vars = json_data['main'][locale_key]['localeDisplayNames']['languages']

            if locale_key in data['languages']:
                if locale_key in language_vars:
                    data['languages'][locale_key].name_local = language_vars[locale_key]

        json_file.close()

    return data
            
def ImportCldrLocalesAndCharacters(cldr_dir, data):
    
    #go through ~709 subdirectories in /main
    for f in os.listdir(cldr_dir+'/json-full/main'):
        (filepath, filename) = os.path.split(f)
    
        json_file = open(cldr_dir+'/json-full/main/'+filename+'/characters.json')
        json_data = json.load(json_file)
        if filename in json_data['main']:
            source = 'cldr '+json_data['main'][filename]['identity']['version']['_cldrVersion']
        
            locale_key = filename

            identity_vars = json_data['main'][locale_key]['identity']
            character_vars = json_data['main'][locale_key]['characters']
        
            identity_language = None
            identity_script = None
            identity_territory = None
            identity_variant = None
        
            if 'language' in identity_vars:
                identity_language = identity_vars['language']
            if 'script' in identity_vars:
                identity_script = identity_vars['script']
            if 'territory' in identity_vars:
                identity_territory = identity_vars['territory']
            if 'variant' in identity_vars:
                identity_variant = identity_vars['variant']

            if locale_key in data['languages']:
                #existing language, add identity metainfo and characters
            
                #deal with some incorrect CLDR identity data - infer from locale key (iu-Cans-CA, en-WS) instead 
                locale_key_parts = locale_key.split('-')
                for locale_key_part in locale_key_parts:
                    if locale_key_part in data['territories'] and locale_key_part != identity_territory:
                        identity_territory = locale_key_part
                    elif locale_key_part in data['scripts'] and locale_key_part != identity_script:
                        identity_script = locale_key_part
            
                data['languages'][locale_key].characters = character_vars
                if identity_script:
                    data['languages'][locale_key].script_disp_id = identity_script
                if identity_territory:
                    data['languages'][locale_key].territory_disp_id = identity_territory
                if identity_variant:
                    data['languages'][locale_key].variant = identity_variant

            else:
                if not locale_key in data['locales']:
                    #new locale
                    loc_lang_id = locale_key.split('-')[0]
                    if loc_lang_id in data['languages']:
                        data['locales'][locale_key] = Locale(id=locale_key, language_id=loc_lang_id, source=source)
                    else:
                        #the case where a locale contains a new language doesn't currently happen
                        pass

                #add identity metainfo and characters to existing locale
                data['locales'][locale_key].characters = character_vars
                if identity_variant:
                    data['locales'][locale_key].variant = identity_variant

    
        json_file.close()

    return data

def InferCldrLocaleNames(data):

    #figure out locale display name
    for key, thisLocale in data['locales'].iteritems():
        locale_key_parts = key.split('-')
        locale_name = data['languages'][thisLocale.language_id].name_en
        locale_name_extras = []
        for k in locale_key_parts:
            if k in data['scripts']:
                locale_name_extras.append(data['scripts'][k].name_en)
                data['locales'][key].script_disp_id = k
            elif k in data['territories']:
                locale_name_extras.append(data['territories'][k].name_en)
                data['locales'][key].territory_disp_id = k
        if len(locale_name_extras) > 0:
             locale_name = locale_name +' ('+(', '.join(locale_name_extras))+')'
        data['locales'][key].name_en = locale_name
    
    return data

def getOrphanLanguages(cldr_dir, data):

    orphanData = {
        'languages': {},
        'locales': {}
    }
    
    #get stuff from territoryInfo
    json_file = open(cldr_dir+'/json-full/supplemental/territoryInfo.json')
    json_data = json.load(json_file)
    territory_vars = json_data['supplemental']['territoryInfo']
    for id, tdict in territory_vars.iteritems():
        if id in data['territories']:
            if 'languagePopulation' in tdict:
                for loc, ldict in tdict['languagePopulation'].iteritems():
                    loc = loc.replace('_', '-')
                    if loc not in data['languages'] and loc not in data['locales']:
                        if '-' in loc:
                            orphanData['locales'][loc] = Locale(id=loc,source='iso639', language_id=loc.split('-')[0])
                        else:
                            orphanData['languages'][loc] = Language(id=loc,source='iso639')

    json_file.close()

    #get stuff from languageData
    json_file2 = open(cldr_dir+'/json-full/supplemental/languageData.json')
    json_data2 = json.load(json_file2)
    language_vars = json_data2['supplemental']['languageData']
    for id, ldict in language_vars.iteritems():
        if '-alt-secondary' in id:
            id = id.replace('-alt-secondary', '')
        #print id
        if id not in data['languages'] and id not in orphanData['languages']:
            orphanData['languages'][id] = Language(id=id,source='iso639')
    
    #add orphan locales to languages
    for orphan in orphanData['locales']:
        orphan = orphan.split('-')[0]
        if orphan not in data['languages'] and orphan not in orphanData['languages']:
            orphanData['languages'][orphan] = Language(id=orphan,source='iso639')

    json_file2.close()

    return orphanData

def getIso639Lookup(iso639_dir):
    
    tab_file_loc = None
    for f in os.listdir(iso639_dir):
        (filepath, filename) = os.path.split(f)
        if 'Name_Index' in filename:
            tab_file_loc = iso639_dir+'/'+filename
            break
    
    iso639Lookup = {}
    
    if tab_file_loc:
        with open(tab_file_loc, 'rb') as f:
            reader = UnicodeReader(f, delimiter='\t')
            for row in reader:
                iso639Lookup[row[0]] = row[1]

    if len(iso639Lookup) > 0:
        return iso639Lookup
    else:
        return None

def getOrphanLanguageNames(iso639_dir, orphanData):

    iso639Lookup = getIso639Lookup(iso639_dir)

    delItems = []
    for key, orphan in orphanData['languages'].iteritems():
        if key in iso639Lookup:
            orphanData['languages'][key].name_en = iso639Lookup[key]
            orphanData['languages'][key].url_name = SanitizeURLName(iso639Lookup[key])
        else:
            delItems.append(key)
            #the TRULY orphaned orphans, currently only http://en.wikipedia.org/wiki/ISO_639:bhk
            pass
            
    for key in delItems:
        del orphanData['languages'][key]

    return orphanData

def ImportCldrOrphanLanguages(iso639_dir, cldr_dir, data):
    
    orphanData = getOrphanLanguages(cldr_dir, data)
    orphanData = getOrphanLanguageNames(iso639_dir, orphanData)

    for key, lang in orphanData['languages'].iteritems():
        data['languages'][key] = lang

    for key, locale in orphanData['locales'].iteritems():
        data['locales'][key] = locale


    return data

def ImportCldrTerritoryContainment(cldr_dir, data):

    #get stuff from territoryInfo
    json_file = open(cldr_dir+'/json-full/supplemental/territoryContainment.json')
    json_data = json.load(json_file)
    territory_vars = json_data['supplemental']['territoryContainment']
    for id, tdict in territory_vars.iteritems():
        if id in data['territories']:
            parent = data['territories'][id]
            if '_contains' in tdict:
                parent.children_territories = tdict['_contains']
                for child in tdict['_contains']:
                    if child in data['territories']:
                        data['territories'][child].parent_territory_id = parent.id

    
    json_file.close()
    return data

def SaveLocaleData(data):

    db.session.query(Script).all()
    db.session.query(Territory).all()

    #save scripts
    for key, script in data['scripts'].iteritems():
        db.session.merge(script)

    #save territories
    for key, territory in data['territories'].iteritems():
        db.session.merge(territory)

    db.session.commit()
    db.session.query(Language).all()
    
    #save languages
    for key, language in data['languages'].iteritems():
        db.session.merge(language)
        
    db.session.commit()    
    db.session.query(Locale).all()

    #save locales
    for key, locale in data['locales'].iteritems():
    #    if locale.language_id in data['languages']:
        db.session.merge(locale)
    #    else:
            #print '*** not found *** '+locale.language_id
    #        pass

    db.session.commit()    
    db.session.query(Language2Territory).all()

    for key, l2t in data['language2territories'].iteritems():
        db.session.merge(l2t)

    db.session.commit()    
    db.session.query(Locale2Territory).all()

    for key, l2t in data['locale2territories'].iteritems():
        db.session.merge(l2t)
        
        
    db.session.commit()
    db.session.query(Language2Script).all()

    for key, l2s in data['language2scripts'].iteritems():
        db.session.merge(l2s)
    
    db.session.commit()
    
    
    return True
    
def SaveParentTerritoryData(data):
    
    db.session.query(Territory).all()
    #save territories
    for key, territory in data['territories'].iteritems():
        db.session.merge(territory)

    db.session.commit()
    return True
    
    
def ImportCldr(cldr_dir, iso639_dir, apple_dir):
    
    #start = time.clock()
    
    #json_results = []
    
    #get json file
    #json_results.append(current_app.config['FONTCATALOG_CLDR_PATH'])
    #json_results.append(current_app.config['FONTCATALOG_CLDR_TEMP_PATH'])
    
    #cldr_dir = current_app.config['FONTCATALOG_CLDR_TEMP_PATH']
    #iso639_dir = current_app.config['FONTCATALOG_ISO639_TEMP_PATH']
    
    localeData = {
        'scripts': {},
        'territories': {},
        'languages': {},
        'locales': {},
        'language2territories': {},
        'locale2territories': {},
        'language2scripts': {}
    }
    
    localeData = ImportCldrMetadata(cldr_dir, localeData)
    localeData = ImportCldrLanguageNames(cldr_dir, localeData)
    localeData = ImportCldrScriptNames(cldr_dir, localeData)
    localeData = ImportCldrMetadataLocales(cldr_dir, localeData)
    localeData = ImportCldrTerritoryNames(cldr_dir, localeData)
    localeData = ImportCldrLocalesAndCharacters(cldr_dir, localeData)
    localeData = ImportCldrLocalLanguageNames(cldr_dir, localeData)    
    localeData = ImportCldrOrphanLanguages(iso639_dir, cldr_dir, localeData)
    localeData = InferCldrLocaleNames(localeData)
    localeData = ImportCldrTerritoryInfo(cldr_dir, localeData)
    localeData = ImportCldrLanguageData(cldr_dir, localeData)
    #localeData = ImportCldrTerritoryContainment(cldr_dir, localeData)
    localeData = ImportAppleScriptMetadata(apple_dir, localeData)
    localeData = ImportAppleLanguageMetadata(apple_dir, localeData)

    #for key, language in localeData['languages'].iteritems():
    #    print language
    
    result = SaveLocaleData(localeData)
 
    #save parent territories after the initial territories are saved to preserve foreign-key relation
    localeData = ImportCldrTerritoryContainment(cldr_dir, localeData)
    result = SaveParentTerritoryData(localeData)
    
    #elapsed = (time.clock() - start)
    #print elapsed
    
    #return jsonify(output=json_results)
    return repr(localeData)


def unzip(zipFilePath, destDir):
    zfile = zipfile.ZipFile(zipFilePath)
    for name in zfile.namelist():
        (dirName, fileName) = os.path.split(name)
        # Check if the directory exisits
        newDir = destDir + '/' + dirName
        if not os.path.exists(newDir):
            os.mkdir(newDir)
        if not fileName == '':
            # file
            fd = open(destDir + '/' + name, 'wb')
            fd.write(zfile.read(name))
            fd.close()
    zfile.close()

class ImportCldrCommand(Command):
    """Import Cldr"""
    
    
    @staticmethod
    def ImportCldrInit():
        
        start = time.clock()
        
        json_results = []
        
        #get json file
        json_results.append(current_app.config['FONTCATALOG_CLDR_PATH'])


        try:
            #unzip json file to temp directory
            tmp_dir = tempfile.mkdtemp()  # create dir
            
            #json_results.append(tmp_dir)
        
            #unzip CLDR
            unzip(current_app.config['FONTCATALOG_CLDR_PATH']+current_app.config['FONTCATALOG_CLDR_FILENAME'], tmp_dir)
        
            #get iso639 zip
            for f in os.listdir(current_app.config['FONTCATALOG_ISO639_PATH']+'/UTF8'):
                (filepath, isofilename) = os.path.split(f)
                #json_results.append(filepath+' '+filename)
                if '.zip' in isofilename:
                    unzip(current_app.config['FONTCATALOG_ISO639_PATH']+'/UTF8/'+isofilename, tmp_dir)
                    break
                    
        
            ImportCldr(tmp_dir, tmp_dir+'/'+isofilename.replace('.zip', ''), current_app.config['FONTCATALOG_APPLE_DATA_PATH'])
        
            #for f in os.listdir(tmp_dir+'/json-full/main'):
            #    (filepath, filename) = os.path.split(f)
            #    json_results.append(filepath+' '+filename)            
            
            
        finally:
            try:
                shutil.rmtree(tmp_dir)  # delete directory
            except OSError as exc:
                if exc.errno != 2:  # code 2 - no such file or directory
                    raise  # re-raise exception


        elapsed = (time.clock() - start)
        print elapsed
        
        
        
        return json_results

    
    def run(self):
        #import_cldr_json = ImportCldrCommand.ImportCldrInit()
        import_cldr_json = {}
        print "import cldr"
        #print json.dumps(import_fonts_json, sort_keys=True, indent=4, separators=(',', ': '))
        print json.dumps(import_cldr_json, sort_keys=True, indent=4, separators=(',', ': '))
'''        
    