import { useState, useRef } from 'react';
import { Button, Container, Fade, Overlay, OverlayTrigger, Popover, Row, Tooltip } from 'react-bootstrap';

const CheckButton = ({ content, cancelContent, onClick, ...props }) => {
    const [open, setOpen] = useState(false);
    const target = useRef(null);

    const handleYes = () => {
        setOpen(false);
        onClick();
    };

    return (
        <>
            <Button ref={target} onClick={() => setOpen(true)} {...props}>
                {content}
            </Button>
            <Overlay placement="right" target={target.current} show={open}>
                {(props) => (
                    <Popover {...props} id="button-popover">
                        <Popover.Title as="h3" className="bg-light">
                            Are you sure?
                        </Popover.Title>
                        <Popover.Content>
                            <Container>
                                <Row className="text text-secondary">{cancelContent}</Row>
                                <Row>
                                    <Button variant="outline-success" onClick={() => handleYes()}>
                                        Yes
                                    </Button>
                                    <Button variant="text text-danger" onClick={() => setOpen(false)}>
                                        No
                                    </Button>
                                </Row>
                            </Container>
                        </Popover.Content>
                    </Popover>
                )}
            </Overlay>
        </>
    );
};

const CopyButton = ({ content, copyContent, ...props }) => {
    const handleClick = () => {
        navigator.clipboard.writeText(copyContent);
    };

    const renderTooltip = (props) => {
        return (
            <Tooltip id="button-tooltip" {...props}>
                Token copied!
            </Tooltip>
        );
    };

    return (
        <OverlayTrigger placement="right" overlay={renderTooltip} rootClose trigger="click">
            <Button onClick={handleClick} {...props}>
                {content}
            </Button>
        </OverlayTrigger>
    );
};

export { CheckButton, CopyButton };
