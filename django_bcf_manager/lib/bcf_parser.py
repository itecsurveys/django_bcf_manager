import xmlschema
from datetime import datetime
import zipfile
import os
import shutil
import glob

DEFAULT_BCF_VERSION = '2.0'
# assuming schema will not change with version as we need schema to read version...


def extract_content_from_bcfzip(filename, snapshots_dir, schemas_dir):
    temp_dir = 'TEMP_EXTRACTED'
    with zipfile.ZipFile(filename, "r") as zip_ref:
        zip_ref.extractall(temp_dir)


    if not os.path.isdir(os.path.join(snapshots_dir)):
        os.mkdir(os.path.join(snapshots_dir))

    # first we need to read version
    version_schema = xmlschema.XMLSchema(os.path.join(schemas_dir, '2.1','version.xsd'))
    version_dict = version_schema.to_dict(os.path.join(temp_dir, 'bcf.version'))
    version = version_dict['@VersionId'] if '@VersionId' in version_dict else DEFAULT_BCF_VERSION

    # then we extract schemas from version
    project_schema = xmlschema.XMLSchema(os.path.join(schemas_dir, version, 'project.xsd'))
    markup_schema = xmlschema.XMLSchema(os.path.join(schemas_dir, version, 'markup.xsd'))
    viewpoint_schema = xmlschema.XMLSchema(os.path.join(schemas_dir, version, 'visinfo.xsd'))

    # getting project info in project.bcfp file
    project = project_schema.to_dict(os.path.join(temp_dir, 'project.bcfp'))
    project['sourcefile'] = os.path.basename(filename)
    ## Adding filename to project info - to keep track of source bcffile for project



    #One subdirectory = one BCF issue containing markup.bcf, viewpoint.bcfv and snapshots
    issues = [o[1] for o in os.walk('./' + temp_dir)][0]
    topics = []
    viewpoints = []
    for issue in issues:
        markup = markup_schema.to_dict(os.path.join(temp_dir, issue, 'markup.bcf'))
        topics.append(markup)
        try:
            viewpoint = viewpoint_schema.to_dict(os.path.join(temp_dir, issue, 'viewpoint.bcfv'))
            viewpoints.append(viewpoint)
        except Exception as e:
            print('Viewpoint exception ' + issue + '  '+ e.message)
            # TODO DEBUG this part seems xmlschema fails on valid Component Element ==> no viewpoints are exported
        #we need to copy snapshots somewhere we can reference them later
        if not os.path.isdir(os.path.join(snapshots_dir, issue)):
            os.mkdir(os.path.join(snapshots_dir, issue))
        for filename in glob.glob(os.path.join(temp_dir, issue,'*.png')):
            shutil.copy(filename, os.path.join(snapshots_dir, issue))

    shutil.rmtree(temp_dir)

    return {'project':project, 'topics': topics, 'viewpoints': viewpoints}

def run():
    schema_dir = '../assets/BCF/Schemas'
    data = extract_content_from_bcfzip('../assets/BCF/examples/Annotations.bcfzip', '../../media/snapshots', schema_dir)
    print('project:')
    print(data['project'])
    print('topics:')
    [print(t) for t in data['topics']]

if __name__ == '__main__':
    start = datetime.now()
    print('start: ', start)
    run()
    end = datetime.now()
    print('end: ', end)

print('Ending')
