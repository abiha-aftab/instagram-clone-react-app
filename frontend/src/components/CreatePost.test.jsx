import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { postAPI } from '../api';
import { renderWithAuth } from '../test/render';
import CreatePost from './CreatePost';

vi.mock('../api', async (importOriginal) => ({
  ...(await importOriginal()),
  postAPI: { create: vi.fn() },
}));

const png = () => new File([new Uint8Array(32)], 'harbour.png', { type: 'image/png' });

async function fillForm(file) {
  const user = userEvent.setup({ applyAccept: false });
  await user.upload(screen.getByLabelText('Photo'), file);
  await user.type(screen.getByLabelText('Title'), 'Harbour');
  await user.type(screen.getByLabelText('Caption'), 'Morning');
  return user;
}

describe('CreatePost', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    URL.createObjectURL = vi.fn(() => 'blob:preview');
    URL.revokeObjectURL = vi.fn();
  });

  it('refuses a non-image file before uploading', async () => {
    renderWithAuth(<CreatePost onClose={() => {}} onCreated={() => {}} />);
    const user = await fillForm(new File(['%PDF'], 'cv.pdf', { type: 'application/pdf' }));

    expect(screen.getByRole('alert')).toHaveTextContent('Use a JPG, PNG, WebP or GIF image.');
    await user.click(screen.getByRole('button', { name: 'Publish' }));
    expect(postAPI.create).not.toHaveBeenCalled();
  });

  it('sends the photo and fields as multipart form data', async () => {
    postAPI.create.mockResolvedValue({ data: { id: 5, is_published: true } });
    const onCreated = vi.fn();
    renderWithAuth(<CreatePost onClose={() => {}} onCreated={onCreated} />);
    const user = await fillForm(png());

    await user.click(screen.getByRole('button', { name: 'Publish' }));
    const form = postAPI.create.mock.calls[0][0];
    expect(form.get('title')).toBe('Harbour');
    expect(form.get('image').name).toBe('harbour.png');
    expect(onCreated).toHaveBeenCalledWith({ id: 5, is_published: true });
  });

  it('shows the server validation message', async () => {
    postAPI.create.mockRejectedValue({ response: { data: { image: ['File too large: the limit is 5 MB.'] } } });
    renderWithAuth(<CreatePost onClose={() => {}} onCreated={() => {}} />);
    const user = await fillForm(png());

    await user.click(screen.getByRole('button', { name: 'Publish' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('File too large');
  });
});
