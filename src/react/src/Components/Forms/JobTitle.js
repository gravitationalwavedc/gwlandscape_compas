import React from 'react';
import { HiOutlinePencil, HiOutlineCheck, HiOutlineX} from 'react-icons/hi';
import EdiText from 'react-editext';
import { useField, useFormikContext }  from 'formik';
import {Form} from 'react-bootstrap';

const EditButton = () => <React.Fragment><HiOutlinePencil /> edit</React.Fragment>;
const SaveButton = () => <HiOutlineCheck/>;
const CancelButton = () => <HiOutlineX/>;


const JobTitle = () => {
    const { values, handleChange } = useFormikContext();
    const [{value: nameValue}, {error: nameError}, {setValue: setNameValue}] = useField('name');
    const [{value: descriptionValue}, _, {setValue: setDescriptionValue}] = useField('description');

    return <React.Fragment>
        <EdiText
            type="text"
            name="name"
            value={nameValue}
            viewProps={{className: 'h2'}}
            onSave={(value) => setNameValue(value)}
            hint="You can use letters, numbers, underscores, and hyphens."
            editButtonContent={<EditButton/>}
            editButtonClassName="edit-button"
            saveButtonContent={<SaveButton/>}
            saveButtonClassName="save-button"
            cancelButtonContent={<CancelButton/>}
            cancelButtonClassName="cancel-button"
            hideIcons
            editOnViewClick
            submitOnUnfocus
            submitOnEnter
        />
        {nameError &&
            <small className="text-danger">
                Invalid name. You can use letters, numbers, underscores, and hyphens.
            </small>}
        <EdiText
            type="text"
            name="description"
            value={descriptionValue}
            onSave={(value) => setDescriptionValue(value)}
            editButtonContent={<EditButton/>}
            editButtonClassName="edit-button"
            saveButtonContent={<SaveButton/>}
            saveButtonClassName="save-button"
            cancelButtonContent={<CancelButton/>}
            cancelButtonClassName="cancel-button"
            hideIcons
            editOnViewClick
            submitOnUnfocus
            submitOnEnter
        />
        <div>
            <Form.Check
                custom
                id="detailedOutput"
                type="switch"
                value={values['detailedOutput']}
                label="Detailed Output"
                name="detailedOutput"
                onChange={handleChange}
                checked={values['detailedOutput']}/>
        </div>

    </React.Fragment>;
};

export default JobTitle;
